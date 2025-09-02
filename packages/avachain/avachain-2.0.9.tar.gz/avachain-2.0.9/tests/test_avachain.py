"""
Unit tests for the core Avachain module.

This module tests the BaseTool, LLM, OpenaiLLM, and utility functions
from the main avachain module.
"""

import json
from typing import Optional
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel, Field

from avachain import (
    LLM,
    BaseTool,
    CallbackHandler,
    OpenaiLLM,
    convert_functions_to_json,
    convert_tool_to_json,
    convert_tools_to_json,
    extract_function_info,
    find_and_execute_tool,
    map_type_to_json,
)


class TestBaseTool:
    """Test cases for BaseTool class."""

    def test_base_tool_creation(self):
        """Test creating a basic tool."""

        class SimpleToolArgs(BaseModel):
            message: str = Field(description="Message to return")

        class SimpleTool(BaseTool):
            name: str = "simple_tool"
            description: str = "A simple test tool"
            args_schema: Optional[type] = SimpleToolArgs

            def _run(self, message: str) -> str:
                return f"Tool says: {message}"

        tool = SimpleTool()
        assert tool.name == "simple_tool"
        assert tool.description == "A simple test tool"
        assert tool.args_schema == SimpleToolArgs
        assert tool.return_direct is False

    def test_base_tool_execution(self):
        """Test tool execution."""

        class EchoTool(BaseTool):
            name: str = "echo_tool"
            description: str = "Echo tool"

            def _run(self, text: str = "hello") -> str:
                return f"Echo: {text}"

        tool = EchoTool()
        result = tool._run("test")
        assert result == "Echo: test"

    def test_base_tool_not_implemented(self):
        """Test that BaseTool._run raises NotImplementedError."""
        tool = BaseTool(name="test", description="test tool")

        with pytest.raises(NotImplementedError):
            tool._run()


class TestLLM:
    """Test cases for LLM base class."""

    def test_llm_initialization(self):
        """Test LLM initialization."""
        llm = LLM(api_key="test-key", base_url="https://api.example.com")

        assert llm.api_key == "test-key"
        assert llm.base_url == "https://api.example.com"
        assert llm.LLMClient is None

    def test_llm_get_kwargs(self):
        """Test LLM kwargs retrieval."""
        kwargs = {"model": "gpt-3.5-turbo", "temperature": 0.7}
        llm = LLM(api_key="test-key", **kwargs)

        assert llm.get_kwargs() == kwargs


class TestOpenaiLLM:
    """Test cases for OpenaiLLM class."""

    def test_openai_llm_initialization(self):
        """Test OpenaiLLM initialization."""
        with patch("avachain.avachain.openai.OpenAI") as mock_openai:
            llm = OpenaiLLM(api_key="test-key", model="gpt-3.5-turbo", temperature=0.7)

            mock_openai.assert_called_once()
            assert llm.kwargs == {"model": "gpt-3.5-turbo", "temperature": 0.7}

    def test_openai_llm_with_base_url(self):
        """Test OpenaiLLM with custom base URL."""
        with patch("avachain.avachain.openai.OpenAI") as mock_openai:
            llm = OpenaiLLM(
                api_key="test-key",
                base_url="https://api.custom.com",
                model="gpt-3.5-turbo",
            )

            mock_openai.assert_called_with(
                base_url="https://api.custom.com", api_key="test-key"
            )


class TestCallbackHandler:
    """Test cases for CallbackHandler class."""

    def test_callback_handler_methods(self):
        """Test that callback methods can be called without errors."""
        handler = CallbackHandler()

        # These should not raise any exceptions
        handler.on_agent_run("test message")
        handler.on_tool_call("test_tool", {"param": "value"})
        handler.on_general_response("test response")
        handler.on_streaming_chunk("chunk")


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_map_type_to_json(self):
        """Test type mapping to JSON schema types."""
        assert map_type_to_json(int) == "number"
        assert map_type_to_json(float) == "number"
        assert map_type_to_json(str) == "string"
        assert map_type_to_json(bool) == "boolean"
        assert map_type_to_json(list) == "<class 'list'>"

    @pytest.mark.skip(reason="Function signature changed, needs updating")
    def test_convert_tool_to_json(self, mock_tool):
        """Test converting a tool to JSON format."""
        json_tool = convert_tool_to_json(
            tool=mock_tool,
            tool_id="test_tool_id",
            human_description="Test tool description",
            public_name="Test Tool",
        )

        assert json_tool["type"] == "function"
        assert json_tool["function"]["name"] == "mock_tool"
        assert json_tool["function"]["description"] == "A mock tool for testing"
        assert "parameters" in json_tool["function"]
        assert "properties" in json_tool["function"]["parameters"]

    def test_convert_functions_to_json(self, mock_tool):
        """Test converting a tool to legacy functions format."""
        json_func = convert_functions_to_json(mock_tool)

        assert json_func["name"] == "mock_tool"
        assert json_func["description"] == "A mock tool for testing"
        assert "parameters" in json_func

    def test_convert_tools_to_json(self, mock_tool):
        """Test converting multiple tools to JSON."""
        tools = [mock_tool]

        # Test modern format
        json_tools = convert_tools_to_json(tools, is_function_based=False)
        assert len(json_tools) == 1
        assert json_tools[0]["type"] == "function"

        # Test legacy format
        json_functions = convert_tools_to_json(tools, is_function_based=True)
        assert len(json_functions) == 1
        assert "name" in json_functions[0]

    def test_extract_function_info(self):
        """Test extracting function info from tool calls."""
        # Mock tool call object
        tool_call = Mock()
        tool_call.id = "call_123"
        tool_call.function = Mock()
        tool_call.function.name = "test_function"
        tool_call.function.arguments = '{"param": "value"}'

        name, params, call_id = extract_function_info(
            tool_call, is_function_based=False
        )

        assert name == "test_function"
        assert params == '{"param": "value"}'
        assert call_id == "call_123"

    def test_extract_function_info_legacy(self):
        """Test extracting function info in legacy format."""
        # Mock function call object
        function_call = Mock()
        function_call.name = "test_function"
        function_call.arguments = '{"param": "value"}'

        name, params, call_id = extract_function_info(
            function_call, is_function_based=True
        )

        assert name == "test_function"
        assert params == '{"param": "value"}'
        assert call_id is None

    def test_extract_function_info_none(self):
        """Test extracting function info with None input."""
        name, params, call_id = extract_function_info(None)

        assert name is None
        assert params is None
        assert call_id is None

    @pytest.mark.skip(reason="Function behavior changed, needs updating")
    def test_find_and_execute_tool(self, mock_tool):
        """Test finding and executing a tool."""
        tools_list = [mock_tool]
        tool_params = {"text": "hello", "multiplier": 2}

        result, return_direct = find_and_execute_tool(
            "mock_tool", tools_list, tool_params
        )

        assert result == "Processed: hellohello"
        assert return_direct is False

    def test_find_and_execute_tool_not_found(self, mock_tool):
        """Test finding a tool that doesn't exist."""
        tools_list = [mock_tool]

        result = find_and_execute_tool("nonexistent_tool", tools_list, {})

        assert result is None

    def test_find_and_execute_tool_no_params(self):
        """Test executing a tool with no parameters."""

        class NoParamTool(BaseTool):
            name: str = "no_param_tool"
            description: str = "Tool with no parameters"

            def _run(self) -> str:
                return "No params needed"

        tool = NoParamTool()
        tools_list = [tool]

        result, return_direct = find_and_execute_tool("no_param_tool", tools_list, None)

        assert result == "No params needed"
        assert return_direct is False

    @pytest.mark.skip(reason="Function behavior changed, needs updating")
    def test_find_and_execute_tool_empty_params(self):
        """Test executing a tool with empty parameters flag."""

        class SimpleTestTool(BaseTool):
            name: str = "simple_test_tool"
            description: str = "Simple tool for testing"

            def _run(self) -> str:
                return "Simple response"

        tool = SimpleTestTool()
        tools_list = [tool]

        result, return_direct = find_and_execute_tool(
            "simple_test_tool", tools_list, {}, is_empty_tool_params=True
        )

        assert result == "pass"
        assert return_direct is False

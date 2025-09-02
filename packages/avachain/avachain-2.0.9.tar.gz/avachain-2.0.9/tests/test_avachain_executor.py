"""
Unit tests for the AvaAgent class and executor functionality.

This module tests the main agent execution logic, message handling,
and tool integration capabilities.
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from conftest import FailingTool, MockTool

from avachain import AvaAgent, CallbackHandler, OpenaiLLM


class TestAvaAgent:
    """Test cases for AvaAgent class."""

    def test_agent_initialization(self, mock_llm, mock_tool):
        """Test basic agent initialization."""
        agent = AvaAgent(
            sys_prompt="You are a test assistant.",
            ava_llm=mock_llm,
            tools_list=[mock_tool],
            agent_name_identifier="test_agent",
        )

        assert agent.sys_prompt == "You are a test assistant."
        assert agent.ava_llm == mock_llm
        assert len(agent.tools_list) == 1
        assert agent.agent_name_identifier == "test_agent"
        assert len(agent.messages) == 1  # System message added
        assert agent.messages[0]["role"] == "system"

    def test_agent_initialization_with_options(self, mock_llm):
        """Test agent initialization with various options."""
        agent = AvaAgent(
            sys_prompt="Test prompt",
            ava_llm=mock_llm,
            tools_list=[],
            pickup_mes_count=10,
            logging=True,
            max_agent_iterations=5,
            streaming=True,
            include_message_timestap=False,
        )

        assert agent.pickup_mes_count == 10
        assert agent.logging is True
        assert agent.max_agent_iterations == 5
        assert agent.streaming is True
        assert agent.include_message_timestap is False

    def test_agent_with_callback_handler(self, mock_llm, mock_tool):
        """Test agent with callback handler."""
        callback_handler = Mock(spec=CallbackHandler)

        agent = AvaAgent(
            sys_prompt="Test prompt",
            ava_llm=mock_llm,
            tools_list=[mock_tool],
            callback_handler=callback_handler,
        )

        assert agent.callback_handler == callback_handler

    def test_append_to_messages(self, sample_agent):
        """Test appending messages to conversation history."""
        initial_count = len(sample_agent.messages)

        sample_agent.appendToMessages("user", "Hello, how are you?")

        assert len(sample_agent.messages) == initial_count + 1
        assert sample_agent.messages[-1]["role"] == "user"
        assert "Hello, how are you?" in sample_agent.messages[-1]["content"]

    def test_append_to_messages_with_timestamp(self, mock_llm, mock_tool):
        """Test appending messages with timestamps."""
        agent = AvaAgent(
            sys_prompt="Test prompt",
            ava_llm=mock_llm,
            tools_list=[mock_tool],
            include_message_timestap=True,
        )

        agent.appendToMessages("user", "Test message")

        # Should contain timestamp
        message_content = agent.messages[-1]["content"]
        assert "SystemNote:" in message_content
        assert "Test message" in message_content

    def test_append_to_messages_without_timestamp(self, mock_llm, mock_tool):
        """Test appending messages without timestamps."""
        agent = AvaAgent(
            sys_prompt="Test prompt",
            ava_llm=mock_llm,
            tools_list=[mock_tool],
            include_message_timestap=False,
        )

        agent.appendToMessages("user", "Test message")

        # Should not contain timestamp
        message_content = agent.messages[-1]["content"]
        assert "SystemNote:" not in message_content
        assert message_content == "Test message"

    @pytest.mark.skip(reason="Trim list behavior changed, needs updating")
    def test_trim_list(self, sample_agent):
        """Test trimming message list to specified count."""
        # Add multiple messages
        for i in range(10):
            sample_agent.messages.append({"role": "user", "content": f"Message {i}"})

        trimmed = sample_agent.trim_list(sample_agent.messages, count=5)

        assert len(trimmed) == 5
        # Should keep system message and most recent messages
        assert trimmed[0]["role"] == "system"
        assert "Message 9" in trimmed[-1]["content"]

    def test_generate_system_prompt_with_context(self, sample_agent):
        """Test generating system prompt with context."""
        original_prompt = sample_agent.sys_prompt
        context = "USER: Hello\nASSISTANT: Hi there!"

        sample_agent.generate_system_prompt_with_context(context)

        assert sample_agent.sys_prompt != original_prompt
        assert context in sample_agent.sys_prompt
        assert sample_agent.sys_prompt_original == original_prompt

        # Test reverting to original
        sample_agent.generate_system_prompt_with_context(None)
        assert sample_agent.sys_prompt == original_prompt

    def test_run_basic(self, sample_agent):
        """Test basic agent run functionality."""
        # Mock the main executor to return a simple response
        with patch.object(
            sample_agent, "ava_main_executor", return_value="Test response"
        ):
            response = sample_agent.run("Hello, agent!")

            assert response == "Test response"
            # Check that message was added
            assert any("Hello, agent!" in str(msg) for msg in sample_agent.messages)

    def test_run_empty_message(self, sample_agent):
        """Test agent run with empty message."""
        with pytest.raises(ValueError, match="Input to agent cannot be blank"):
            sample_agent.run("")

        with pytest.raises(ValueError, match="Input to agent cannot be blank"):
            sample_agent.run(None)

    def test_run_with_actual_mes(self, sample_agent):
        """Test agent run with actual_mes parameter."""
        with patch.object(
            sample_agent, "ava_main_executor", return_value="Test response"
        ):
            response = sample_agent.run(
                "Display message", actual_mes="Internal message"
            )

            assert response == "Test response"
            # Should use actual_mes in conversation
            assert any("Internal message" in str(msg) for msg in sample_agent.messages)

    def test_run_with_context_history(self, mock_llm, mock_tool):
        """Test agent run with context history enabled."""
        agent = AvaAgent(
            sys_prompt="Test prompt",
            ava_llm=mock_llm,
            tools_list=[mock_tool],
            use_system_prompt_as_context=True,
            include_message_timestap=True,
        )

        with patch.object(agent, "ava_main_executor", return_value="Test response"):
            agent.run("Hello!")

            # Context history should be updated
            assert "USER" in agent.system_prompt_contexts_history
            assert "Hello!" in agent.system_prompt_contexts_history

    def test_ava_main_executor_success(self, sample_agent):
        """Test successful main executor execution."""
        with patch.object(
            sample_agent, "handle_openai_llm_completions", return_value="Success"
        ):
            result = sample_agent.ava_main_executor(
                messages=[{"role": "user", "content": "test"}],
                tools_list=sample_agent.tools_list,
                ava_llm=sample_agent.ava_llm,
            )

            assert result == "Success"
            assert sample_agent.current_agent_iteration == 1

    def test_ava_main_executor_max_iterations(self, sample_agent):
        """Test main executor with maximum iterations exceeded."""
        sample_agent.current_agent_iteration = sample_agent.max_agent_iterations + 1

        result = sample_agent.ava_main_executor(
            messages=[{"role": "user", "content": "test"}],
            tools_list=sample_agent.tools_list,
            ava_llm=sample_agent.ava_llm,
        )

        assert "wasn't able to complete" in result
        assert sample_agent.current_agent_iteration == 0  # Should reset

    def test_ava_main_executor_max_iterations_with_error(self, mock_llm, mock_tool):
        """Test main executor with error on max iterations."""
        agent = AvaAgent(
            sys_prompt="Test prompt",
            ava_llm=mock_llm,
            tools_list=[mock_tool],
            throw_error_on_iteration_exceed=True,
        )

        agent.current_agent_iteration = agent.max_agent_iterations + 1

        with pytest.raises(ValueError, match="exceeded the max agent iteration count"):
            agent.ava_main_executor(
                messages=[{"role": "user", "content": "test"}],
                tools_list=agent.tools_list,
                ava_llm=agent.ava_llm,
            )

    def test_ava_main_executor_invalid_params(self, sample_agent):
        """Test main executor with invalid parameters."""
        sample_agent.messages = []  # Empty messages

        with pytest.raises(ValueError, match="Check the passed message"):
            sample_agent.ava_main_executor(
                messages=[],
                tools_list=sample_agent.tools_list,
                ava_llm=sample_agent.ava_llm,
            )

    def test_ava_main_executor_with_callback(self, mock_llm, mock_tool):
        """Test main executor with callback handler."""
        callback_handler = Mock(spec=CallbackHandler)
        callback_handler.on_agent_run = Mock()

        agent = AvaAgent(
            sys_prompt="Test prompt",
            ava_llm=mock_llm,
            tools_list=[mock_tool],
            callback_handler=callback_handler,
        )

        with patch.object(
            agent, "handle_openai_llm_completions", return_value="Success"
        ):
            agent.ava_main_executor(
                messages=[{"role": "user", "content": "test"}],
                tools_list=agent.tools_list,
                ava_llm=agent.ava_llm,
            )

            # Callback should have been called
            callback_handler.on_agent_run.assert_called_once_with(
                input_msg="agent started running!"
            )

    def test_validate_and_append_to_list_user(self, sample_agent):
        """Test validating and appending user message."""
        initial_count = len(sample_agent.messages)

        sample_agent.validate_and_append_to_list(role="user", content="Hello, world!")

        assert len(sample_agent.messages) == initial_count + 1
        new_message = sample_agent.messages[-1]
        assert new_message["role"] == "user"
        assert new_message["content"] == "Hello, world!"

    def test_validate_and_append_to_list_assistant(self, sample_agent):
        """Test validating and appending assistant message."""
        sample_agent.validate_and_append_to_list(
            role="assistant", content="Hello there!"
        )

        new_message = sample_agent.messages[-1]
        assert new_message["role"] == "assistant"
        assert new_message["content"] == "Hello there!"

    def test_validate_and_append_to_list_tool(self, sample_agent):
        """Test validating and appending tool message."""
        sample_agent.validate_and_append_to_list(
            role="tool",
            content="Tool result",
            tool_call_id="call_123",
            tool_name="test_tool",
        )

        new_message = sample_agent.messages[-1]
        assert new_message["role"] == "tool"
        assert new_message["content"] == "Tool result"
        assert new_message["tool_call_id"] == "call_123"


class TestAvaAgentIntegration:
    """Integration tests for AvaAgent functionality."""

    @pytest.mark.slow
    def test_agent_with_mock_llm_response(self, mock_tool):
        """Test agent with mocked LLM response."""
        # Create a mock LLM
        mock_llm = Mock(spec=OpenaiLLM)
        mock_llm.ava_llm_completions = Mock()

        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "I understand your request."
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"

        mock_llm.ava_llm_completions.return_value = mock_response

        agent = AvaAgent(
            sys_prompt="You are a helpful assistant.",
            ava_llm=mock_llm,
            tools_list=[mock_tool],
            logging=False,
        )

        # This should work without making real API calls
        with patch.object(agent, "isOpenaiLLM", True):
            response = agent.run("Hello, how can you help me?")

            assert "understand" in response.lower()

    def test_agent_error_handling(self, sample_agent):
        """Test agent error handling during execution."""
        # Make the main executor raise an exception
        with patch.object(
            sample_agent, "ava_main_executor", side_effect=ValueError("Test error")
        ):
            with pytest.raises(ValueError, match="Error in agent run"):
                sample_agent.run("This should fail")

    def test_agent_with_failing_tool(self, mock_llm):
        """Test agent behavior with a failing tool."""
        failing_tool = FailingTool()

        agent = AvaAgent(
            sys_prompt="You are a test assistant.",
            ava_llm=mock_llm,
            tools_list=[failing_tool],
            logging=False,
        )

        # The agent should handle tool failures gracefully
        assert len(agent.converted_tools_list) == 1
        assert agent.converted_tools_list[0]["function"]["name"] == "failing_tool"

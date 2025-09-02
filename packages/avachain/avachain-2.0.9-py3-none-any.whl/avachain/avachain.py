"""
Avachain - A lightweight library for creating and running AI agents with tools.

This module provides the core classes and utilities for building AI agents that can
interact with OpenAI-compatible Language Learning Models (LLMs). It focuses on
providing a minimal, efficient interface for tool-based agent interactions.
"""

from typing import Any, Dict, List, Optional, Type

import openai
from openai.types.chat import ChatCompletion
from print_color import print
from pydantic import BaseModel, Field
from pydantic_core import PydanticUndefined


class BaseTool(BaseModel):
    """
    Base class for all AI agent tools.

    This class defines the standard interface for tools that can be used by AI agents.
    All custom tools should inherit from this class and implement the _run method.

    Attributes:
        name (str): Unique identifier for the tool
        description (str): Human-readable description of what the tool does
        args_schema (Type[BaseModel], optional): Pydantic model defining the tool's input schema
        return_direct (bool): Whether to return the tool's output directly as the final answer
        agent_obj (Any, optional): Reference to the agent object using this tool
    """

    name: str = Field(description="Name of the tool.")
    description: str = Field(description="Description of the tool.")
    args_schema: Optional[Type[BaseModel]] = Field(
        description="Schema for the tool arguments.", default=None
    )
    return_direct: Optional[bool] = Field(
        description="Whether to return direct the tool response as final answer to a message?",
        default=False,
    )
    agent_obj: Optional[Any] = Field(
        description="Agent object to be used for tool execution.",
        default=None,
    )

    def _run(self, *args, **kwargs):
        """
        Execute the tool with the provided arguments.

        This method must be implemented by subclasses to define the tool's behavior.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses should implement this method.")

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True


class LLM:
    """
    Base Large Language Model (LLM) class.

    This abstract base class provides a common interface for different LLM providers.
    It allows for creating specialized LLM implementations while maintaining consistency
    across different providers like OpenAI, Mistral AI, and Claude.

    Attributes:
        api_key (str): API key for the LLM service
        base_url (str, optional): Custom base URL for the LLM API endpoint
        kwargs: Additional configuration parameters specific to each LLM provider
        LLMClient: The initialized client instance for the specific LLM provider
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        """
        Initialize the LLM with basic parameters.

        Args:
            api_key (str): API key for authentication with the LLM service
            base_url (str, optional): Custom base URL for API endpoints
            **kwargs: Additional provider-specific configuration parameters
        """
        self.api_key = api_key
        self.base_url = base_url
        self.kwargs = kwargs
        self.LLMClient = None

    def set_client(self):
        """
        Initialize the LLM client.

        This method should be implemented by subclasses to set up the specific
        client instance for their respective LLM provider.
        """
        pass

    def get_kwargs(self):
        """
        Get the configuration parameters.

        Returns:
            dict: Configuration parameters for the LLM
        """
        return self.kwargs

    def ava_llm_completions(
        self, messages: List, tools: List, is_function_based: bool = False, **extras
    ) -> Any:
        """
        Generate completions from the LLM.

        This method provides the main interface for getting responses from the LLM,
        with support for tool usage and function calling.

        Args:
            messages (List): List of conversation messages
            tools (List): List of available tools for the LLM
            is_function_based (bool): Whether to use function-based tool calling
            **extras: Additional parameters for the completion request

        Returns:
            Any: Completion response from the LLM
        """
        pass


class OpenaiLLM(LLM, openai.OpenAI):
    """
    OpenAI Language Learning Model implementation.

    This class provides integration with OpenAI's API and OpenAI-compatible APIs.
    It supports both standard completions and streaming responses, with full
    support for tool calling and function-based interactions.

    Attributes:
        LLMClient: OpenAI client instance for API communication
        kwargs: Configuration parameters for the OpenAI API calls
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        """
        Initialize the OpenAI LLM client.

        Args:
            api_key (str): OpenAI API key for authentication
            base_url (str, optional): Custom base URL for OpenAI-compatible APIs
            **kwargs: Additional configuration parameters (model, temperature, etc.)
        """
        self.kwargs = kwargs
        if base_url:
            self.LLMClient: openai = openai.OpenAI(base_url=base_url, api_key=api_key)
        else:
            self.LLMClient: openai = openai.OpenAI(api_key=api_key)

    def get_kwargs(self):
        return self.kwargs

    def ava_llm_completions(
        self,
        messages: List,
        tools: List,
        is_function_based: bool = False,
        streaming: bool = False,
        logging: bool = False,
        tool_choice: str = None,
    ) -> ChatCompletion:
        """
        Generate completions using the OpenAI LLM with tool support.

        This method handles standard (non-streaming) completions from OpenAI models,
        with support for both modern tool calling and legacy function calling formats.
        It automatically configures the request parameters based on the provided tools
        and calling convention.

        Args:
            messages (List): List of conversation messages in OpenAI format
            tools (List): List of available tools for the LLM to use
            is_function_based (bool): Whether to use legacy function format (deprecated)
            streaming (bool): Whether to enable streaming (handled by other methods)
            logging (bool): Whether to enable detailed logging (currently unused)
            tool_choice (str, optional): Tool choice strategy ("auto", "none", or specific tool)

        Returns:
            ChatCompletion: OpenAI completion response object

        Example:
            >>> messages = [{"role": "user", "content": "What's the weather?"}]
            >>> response = openai_llm.ava_llm_completions(messages, tools)
        """
        # Set up the base parameters from kwargs
        self.kwargs["messages"] = messages
        self.kwargs["stream"] = streaming

        # Configure tools if provided
        if tools != []:
            if not is_function_based:
                # Use modern tool calling format
                self.kwargs["tools"] = tools
            else:
                # Use legacy function calling format (deprecated)
                self.kwargs["functions"] = tools

        # Generate and return the completion
        chat_completion = self.LLMClient.chat.completions.create(**self.kwargs)
        return chat_completion

    def ava_chain_llm_completions(
        self,
        messages: List,
        tools: List,
        is_function_based: bool = False,
        streaming: bool = False,
        logging: bool = False,
    ) -> ChatCompletion:
        """
        Generate completions for chain-based operations.

        This method provides completions specifically designed for chained or
        sequential operations, though it currently mirrors the standard completion
        functionality. It's maintained separately to allow for future chain-specific
        optimizations and features.

        Args:
            messages (List): List of conversation messages
            tools (List): List of available tools
            is_function_based (bool): Whether to use legacy function format
            streaming (bool): Whether to enable streaming
            logging (bool): Whether to enable logging

        Returns:
            ChatCompletion: OpenAI completion response
        """
        # Configure request parameters
        self.kwargs["messages"] = messages
        self.kwargs["stream"] = streaming

        # Set up tools based on calling convention
        if tools != []:
            if not is_function_based:
                self.kwargs["tools"] = tools
            else:
                self.kwargs["functions"] = tools

        # Generate and return completion
        chat_completion = self.LLMClient.chat.completions.create(**self.kwargs)
        return chat_completion

    def ava_llm_streaming_completions(
        self,
        messages: List,
        tools: List,
        is_function_based: bool = False,
        streaming: bool = False,
        logging: bool = False,
    ) -> ChatCompletion:
        """
        Generate streaming completions from the OpenAI LLM.

        This method provides real-time streaming responses from the LLM, allowing
        for interactive conversations and real-time processing. It yields response
        chunks as they become available from the model.

        Args:
            messages (List): List of conversation messages
            tools (List): List of available tools for the LLM
            is_function_based (bool): Whether to use legacy function format
            streaming (bool): Whether streaming is enabled (automatically set to True)
            logging (bool): Whether to enable detailed logging

        Returns:
            ChatCompletion: Async generator that yields response chunks

        Example:
            >>> async for chunk in openai_llm.ava_llm_streaming_completions(messages, tools):
            ...     print(chunk.decode('utf-8'), end='')
        """
        # Configure streaming parameters
        self.kwargs["messages"] = messages
        self.kwargs["stream"] = streaming

        # Set up tools if provided
        if tools != []:
            if not is_function_based:
                self.kwargs["tools"] = tools
            else:
                self.kwargs["functions"] = tools

        # Define the streaming generator function
        async def stream():
            """
            Async generator that yields streaming response chunks.

            Yields:
                bytes: Encoded response chunks from the LLM

            Raises:
                ValueError: If an error occurs during streaming
            """
            try:
                # Create the streaming completion
                completion = self.LLMClient.chat.completions.create(**self.kwargs)

                # Process each chunk in the stream
                for line in completion:
                    chunk = None
                    if line.choices[0]:
                        chunk = line.choices[0].delta.content
                    if chunk:
                        # Yield the chunk as bytes with newline separator
                        yield chunk.encode("utf-8") + b"\n"
            except Exception as e:
                print(f"An error occurred in streaming: {str(e)}")
                raise ValueError(
                    "An error occurred while making request to streaming endpoint: ", e
                )

        return stream()


class CallbackHandler:
    """
    Callback handler for agent events and interactions.

    This class provides hooks for monitoring and responding to various events
    during agent execution, including tool calls, responses, and streaming chunks.
    """

    def on_agent_run(self, input_msg: str):
        """
        Called when the agent starts processing a new input message.

        Args:
            input_msg (str): The input message being processed
        """
        pass

    def on_tool_call(self, tool_name: str, tool_params: Dict):
        """
        Called when the agent invokes a tool.

        Args:
            tool_name (str): Name of the tool being called
            tool_params (Dict): Parameters passed to the tool
        """
        pass

    def on_general_response(self, response: str):
        """
        Called when the agent generates a general response.

        Args:
            response (str): The response content
        """
        pass

    def on_streaming_chunk(self, chunk: str):
        """
        Called for each streaming chunk received from the LLM.

        Args:
            chunk (str): The streaming chunk content
        """
        pass


def map_type_to_json(type_info):
    """
    Map Python types to JSON schema types.

    This function converts Python built-in types to their corresponding
    JSON schema type strings for API compatibility.

    Args:
        type_info: Python type object (int, float, str, bool, etc.)

    Returns:
        str: JSON schema type string ("number", "string", "boolean", etc.)
    """
    type_mappings = {
        int: "number",
        float: "number",
        str: "string",
        bool: "boolean",
    }
    return type_mappings.get(type_info, str(type_info))


def convert_tool_to_json(
    tool: BaseTool,
) -> Dict[str, Any]:
    """
    Convert a BaseTool object into OpenAI-compatible JSON format.

    This function transforms a BaseTool instance into the JSON schema format
    required by OpenAI's function calling API. It extracts the tool's metadata,
    arguments schema, and creates the appropriate JSON structure.

    Args:
        tool (BaseTool): The tool object to convert

    Returns:
        Dict[str, Any]: JSON representation compatible with OpenAI function calling

    Example:
        >>> tool = MyCustomTool(name="search", description="Search the web")
        >>> json_tool = convert_tool_to_json(tool)
        >>> # Returns: {"type": "function", "function": {"name": "search", ...}}
    """
    json_representation = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    required_args = []
    if tool.args_schema:
        for field_name, field_info in tool.args_schema.__annotations__.items():
            field_description = getattr(
                tool.args_schema.model_fields[field_name],
                "description",
                "No description available",
            )

            field_properties = {
                "type": map_type_to_json(field_info),
                "description": field_description,
            }
            if tool.args_schema.model_fields[field_name].repr:
                required_args.append(str(field_name))

            default_value = tool.args_schema.model_fields[field_name].default
            if default_value is not None and default_value is not PydanticUndefined:
                field_properties["default"] = default_value

            enums_present = tool.args_schema.model_fields[field_name].json_schema_extra

            if enums_present:
                enum_values = enums_present.get("enumerate", None)

                if enum_values is not None:
                    field_properties["enum"] = enum_values

            json_representation["function"]["parameters"]["properties"][
                field_name
            ] = field_properties

            json_representation["function"]["parameters"]["required"] = required_args

    return json_representation


def convert_functions_to_json(
    tool: BaseTool,
) -> Dict[str, Any]:
    """
    Convert a tool object into a JSON representation.

    Args:
        tool (BaseTool): The tool object.

    Returns:
        Dict[str, Any]: JSON representation of the tool.
    """
    json_representation = {
        "name": tool.name,
        "description": tool.description,
        "parameters": {"type": "object", "properties": {}, "required": []},
    }

    required_args = []

    if tool.args_schema:
        for field_name, field_info in tool.args_schema.__annotations__.items():
            field_description = getattr(
                tool.args_schema.model_fields[field_name],
                "description",
                "No description available",
            )

            field_properties = {
                "type": map_type_to_json(field_info),
                "description": field_description,
            }
            if tool.args_schema.model_fields[field_name].repr:
                required_args.append(str(field_name))

            default_value = tool.args_schema.model_fields[field_name].default
            if default_value is not None and default_value is not PydanticUndefined:
                field_properties["default"] = default_value

            enums_present = tool.args_schema.model_fields[field_name].json_schema_extra
            if enums_present:
                enum_values = enums_present.get("enumerate", None)

                if enum_values is not None:
                    field_properties["enum"] = enum_values

            json_representation["parameters"]["properties"][
                field_name
            ] = field_properties
            json_representation["parameters"]["required"] = required_args

    return json_representation


def convert_tools_to_json(
    tools: List[BaseTool], is_function_based: bool = False
) -> List[Dict[str, Any]]:
    """
    Convert a list of BaseTool objects into OpenAI-compatible JSON format.

    This function processes multiple tools and converts them into the appropriate
    JSON schema format for OpenAI's function calling API. It supports both
    modern tool calling and legacy function calling formats.

    Args:
        tools (List[BaseTool]): List of tool objects to convert
        is_function_based (bool): Whether to use legacy function format (deprecated)

    Returns:
        List[Dict[str, Any]]: List of JSON representations compatible with OpenAI API

    Example:
        >>> tools = [search_tool, calculator_tool]
        >>> json_tools = convert_tools_to_json(tools)
        >>> # Returns: [{"type": "function", "function": {...}}, ...]
    """
    json_representations = []
    if not is_function_based:
        for tool in tools:
            json_representation = convert_tool_to_json(tool)
            json_representations.append(json_representation)
    else:
        for tool in tools:
            json_representation = convert_functions_to_json(tool)
            json_representations.append(json_representation)

    return json_representations


def extract_function_info(tool_call=None, is_function_based: bool = False):
    """
    Extract function information from LLM tool call response.

    This function parses the tool call object returned by the LLM and extracts
    the function name, parameters, and call ID for execution.

    Args:
        tool_call: Tool call object from LLM response
        is_function_based (bool): Whether using legacy function format

    Returns:
        tuple: (function_name, parameters, call_id) extracted from tool call

    Example:
        >>> name, params, call_id = extract_function_info(tool_call)
        >>> # Returns: ("search_web", '{"query": "python"}', "call_123")
    """
    if tool_call:
        if not is_function_based:
            if tool_call.function:
                function_info = tool_call.function
                name = function_info.name
                params = function_info.arguments
                id = tool_call.id
                return name, params, id
        else:
            name = tool_call.name
            params = tool_call.arguments
            id = None
            return name, params, id

    return None, None, None


def find_and_execute_tool(
    tool_name: str,
    tools_list: List[BaseTool],
    tool_params: Optional[Dict[str, str]] = None,
    is_empty_tool_params: bool = False,
):
    """
    Find and execute a tool by name from the available tools list.

    This function searches through the provided tools list to find a tool with
    the matching name, then executes it with the provided parameters.

    Args:
        tool_name (str): Name of the tool to execute
        tools_list (List[BaseTool]): List of available tools
        tool_params (Dict[str, str], optional): Parameters to pass to the tool
        is_empty_tool_params (bool): Whether the tool parameters are empty

    Returns:
        tuple: (tool_response, return_direct_flag) - The tool's output and whether
               it should be returned directly as the final answer

    Raises:
        ValueError: If the specified tool is not found in the tools list

    Example:
        >>> response, is_direct = find_and_execute_tool(
        ...     "search_web",
        ...     tools_list,
        ...     {"query": "python"}
        ... )
    """
    for tool in tools_list:
        if tool.name == tool_name:
            if tool_params:
                if is_empty_tool_params:
                    return "pass", tool.return_direct

                args_model = tool.args_schema(**tool_params)
                return tool._run(**args_model.dict()), tool.return_direct
            else:
                return tool._run(), tool.return_direct
    return None

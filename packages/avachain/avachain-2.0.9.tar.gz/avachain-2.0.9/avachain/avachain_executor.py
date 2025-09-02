"""
Avachain Executor - Core agent execution engine.

This module contains the main AvaAgent class that orchestrates the interaction
between users, LLMs, and tools. It provides a streamlined interface for
creating and running AI agents with OpenAI-compatible models.
"""

import json
import time
from datetime import datetime
from traceback import print_exc
from typing import Dict, List, Optional

from print_color import print

from avachain import (
    LLM,
    BaseTool,
    CallbackHandler,
    OpenaiLLM,
    convert_tools_to_json,
    extract_function_info,
    find_and_execute_tool,
)


def get_current_timestamp():
    """
    Get the current timestamp formatted with day of week.

    This function generates a human-readable timestamp that includes the day
    of the week along with the date and time. It's used throughout the system
    for logging and message timestamping.

    Returns:
        str: Formatted timestamp string in the format "DayName, YYYY-MM-DD HH:MM:SS"

    Example:
        >>> get_current_timestamp()
        'Monday, 2024-01-15 14:30:25'
    """
    current_timestamp = datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S")
    return current_timestamp


class AvaAgent:
    """
    Main AI Agent class for executing conversations with tool support.

    AvaAgent orchestrates interactions between users, Language Learning Models (LLMs),
    and tools. It manages conversation history, handles tool calls, and provides
    a streamlined interface for building AI agents.
    """

    def __init__(
        self,
        sys_prompt: str,
        ava_llm: LLM,
        tool_choice: str = None,
        tools_list: Optional[List[BaseTool]] = None,
        pickup_mes_count: int = 4,
        logging: bool = False,
        use_system_prompt_as_context: bool = False,
        is_function_based: bool = False,
        max_agent_iterations: int = 4,
        throw_error_on_iteration_exceed: bool = False,
        callback_handler: CallbackHandler = None,
        agent_name_identifier: str = "agent",
        deeper_logs: bool = False,
        include_message_timestap: bool = True,
        streaming: bool = False,
        pikcup_mes_count_in_sys_history: int = 3,
        tts_streaming: bool = False,
        is_non_gpt_model: bool = False,
        print_tts_streaming: bool = True,
    ):
        """
        Initialize an AvaAgent instance.

        Args:
            sys_prompt (str): System prompt defining agent behavior
            ava_llm (LLM): Language model instance to use
            tool_choice (str, optional): Tool choice strategy
            tools_list (List[BaseTool]): List of available tools
            pickup_mes_count (int): Number of messages to keep in context
            logging (bool): Enable detailed logging
            use_system_prompt_as_context (bool): Use system prompt for context
            is_function_based (bool): Use legacy function calling format
            max_agent_iterations (int): Maximum tool call iterations
            throw_error_on_iteration_exceed (bool): Throw error on max iterations
            callback_handler (CallbackHandler): Handler for agent events
            agent_name_identifier (str): Identifier for logging
            deeper_logs (bool): Enable verbose logging
            include_message_timestap (bool): Include timestamps in messages
            streaming (bool): Enable streaming responses
            pikcup_mes_count_in_sys_history (int): Messages count for system history
            tts_streaming (bool): Enable TTS streaming (deprecated)
            is_non_gpt_model (bool): Whether using non-GPT model
            print_tts_streaming (bool): Print TTS streaming info (deprecated)
        """
        self.include_message_timestap = include_message_timestap
        self.use_system_prompt_as_context = use_system_prompt_as_context
        self.is_function_based = is_function_based
        self.sys_prompt_original = sys_prompt
        self.sys_prompt: str = sys_prompt
        self.messages: List = []
        self.tools_list: List = tools_list if tools_list is not None else []
        self.ava_llm: LLM = ava_llm
        self.pickup_mes_count: int = pickup_mes_count
        self.pikcup_mes_count_in_sys_history = pikcup_mes_count_in_sys_history
        self.isOpenaiLLM = isinstance(self.ava_llm, OpenaiLLM)
        self.is_non_gpt_model = is_non_gpt_model
        if use_system_prompt_as_context:
            self.pickup_mes_count = pikcup_mes_count_in_sys_history
            self.system_prompt_contexts_history = """"""
            self.generate_system_prompt_with_context(
                self.system_prompt_contexts_history
            )
        self.agent_name_identifier = agent_name_identifier
        self.current_user_msg: str = None

        self.appendToMessages(role="system", content=sys_prompt)

        self.converted_tools_list: List[Dict] = convert_tools_to_json(
            tools=tools_list, is_function_based=self.is_function_based
        )
        self.logging: bool = logging
        self.deeper_logs = deeper_logs
        self.callback_handler: CallbackHandler = callback_handler
        self.throw_error_on_iteration_exceed: bool = throw_error_on_iteration_exceed
        self.max_agent_iterations: int = max_agent_iterations
        self.current_agent_iteration: int = 0
        self.streaming: bool = streaming
        self.tts_streaming = tts_streaming
        self.tool_choice = tool_choice
        self.print_tts_streaming = print_tts_streaming
        print(f"{agent_name_identifier} TOOlS:")
        if self.deeper_logs:
            for json_representation in self.converted_tools_list:
                print(json.dumps(json_representation, indent=2))

    def run(
        self,
        msg: str = None,
        actual_mes: Optional[str] = None,
        image_input: Optional[str] = None,
    ):
        """
        Execute the agent with a user message and optional context.

        This is the main entry point for agent execution. It processes user input,
        manages conversation history, handles context if configured, and orchestrates
        the interaction between the user, LLM, and available tools.

        Args:
            msg (str): The user's input message to process
            actual_mes (str, optional): Alternative message content for internal processing
            image_input (str, optional): Image input data (base64 encoded or URL)

        Returns:
            Any: The agent's response, which could be text, tool output, or streaming data

        Raises:
            ValueError: If no input message is provided or if execution fails

        Example:
            >>> agent = AvaAgent(sys_prompt="You are helpful", ava_llm=llm)
            >>> response = agent.run("What's the weather like today?")
        """
        # Validate input
        if not msg:
            raise ValueError("Input to agent cannot be blank")

        try:
            # Display execution start message
            print(
                f"\nRunning {self.agent_name_identifier} ... with input: '{msg}'\n",
                color="purple",
            )

            # Use actual_mes if provided, otherwise use msg
            content = actual_mes if actual_mes else msg

            # Add the user message to conversation history
            self.appendToMessages(role="user", content=content, image_input=image_input)

            # Update system prompt context if enabled
            if self.use_system_prompt_as_context:
                timestamp = (
                    f"(SystemNote:{get_current_timestamp()}): "
                    if self.include_message_timestap
                    else ": "
                )
                # Append user message to context history
                self.system_prompt_contexts_history += f"\nUSER{timestamp}{msg}"

            # Store current user message for reference
            self.current_user_msg = msg

            # Trim message history to manage context length
            self.messages = self.trim_list(
                input_list=self.messages, count=self.pickup_mes_count
            )

            # Execute the main agent processing
            return self.ava_main_executor(
                messages=self.messages,
                tools_list=self.tools_list,
                ava_llm=self.ava_llm,
            )

        except ValueError as e:
            if self.logging:
                print_exc()
            raise ValueError(f"Error in agent run: {e}")

    def generate_system_prompt_with_context(self, context_string=None):
        r"""
        Generate and update the system prompt with conversational context.

        This method enhances the original system prompt by including previous
        conversation history as context. It's used when use_system_prompt_as_context
        is enabled to maintain conversational awareness across interactions.

        Args:
            context_string (str, optional): The conversation history to include.
                                          If None, reverts to original system prompt.

        Note:
            This updates the agent's sys_prompt attribute directly, affecting
            all subsequent interactions until changed again.

        Example:
            >>> agent.generate_system_prompt_with_context("USER: Hello\nASSISTANT: Hi there!")
        """
        if context_string:
            # Create enhanced system prompt with context
            self.sys_prompt = f"""{self.sys_prompt_original}

            Please take into account the preceding and ongoing dialogues between you and the user for context, and utilize this information to inform your subsequent responses.
            Below are the prior and current converstations between you and the user (with message SystemNote). Use it as context and information in further conversations with the User:
            {context_string}
            """
        else:
            # Revert to original system prompt
            self.sys_prompt = self.sys_prompt_original

    def appendToMessages(
        self,
        role: str,
        content: str,
        image_input: Optional[str] = None,
        tool_call_id: Optional[str] = None,
        tool_name: Optional[str] = None,
    ):
        """
        Append a new message to the conversation history.

        This method adds messages to the conversation history in the proper format
        for the configured LLM. It handles different message types (user, assistant,
        system, tool) and includes metadata like timestamps when configured.

        Args:
            role (str): The role of the message sender ("user", "assistant", "system", "tool")
            content (str): The content of the message
            image_input (str, optional): Base64 encoded image data or image URL
            tool_call_id (str, optional): ID of the tool call (for tool response messages)
            tool_name (str, optional): Name of the tool being called

        Note:
            - Automatically adds timestamps to user messages if enabled
            - Handles different message formats based on LLM provider
            - Validates message structure before appending

        Example:
            >>> agent.appendToMessages("user", "Hello, how are you?")
            >>> agent.appendToMessages("tool", "Weather: 75°F", tool_call_id="call_123")
        """
        print(
            self.agent_name_identifier.capitalize(),
            ": ",
            "appending message: Currently LLM is openai? ",
            self.isOpenaiLLM,
        )

        # Add timestamp to user messages if configured
        if role == "user" and self.include_message_timestap:
            content = f"(SystemNote:{get_current_timestamp()}) " + content

        # Handle message formatting based on LLM provider
        if self.isOpenaiLLM:
            self.validate_and_append_to_list(
                role=role,
                content=content,
                image_input=image_input,
                tool_name=tool_name,
                tool_call_id=tool_call_id,
            )

    def validate_and_append_to_list(
        self,
        role,
        content,
        image_input: Optional[str] = None,
        tool_call_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        function_arguments: Optional[str] = None,
    ):
        """
        Validates and appends a new dictionary to the provided list, ensuring JSON compliance.

        Args:
            role (str): The role to add (e.g., "user", "developer", "system").
            content (str): The content to add.
            data_list (list): The existing list of dictionaries to which the new entry will be appended.

        Returns:
            list: The updated list with the new entry, validated and JSON-compliant.

        Raises:
            ValueError: If validation fails for the new entry or the updated list.
        """
        try:
            if not isinstance(role, str):
                raise ValueError("Role must be a string.")
            if role.strip() == "":
                raise ValueError("Role cannot be an empty string.")

            if not isinstance(content, str):
                content = str(content)

            content = "".join(
                char for char in content if 32 <= ord(char) <= 126
            ).strip()

            safe_content = json.dumps(content)[1:-1]

            if image_input:
                new_entry = {
                    "role": role,
                    "content": [
                        {"type": "text", "text": safe_content},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"{image_input}"},
                        },
                    ],
                }
            else:

                if tool_call_id:
                    new_entry = {
                        "role": role,
                        "tool_call_id": tool_call_id,
                        "tool_name": tool_name,
                        "content": safe_content,
                    }
                elif tool_call_id and role == "assistant":
                    new_entry = {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tool_call_id,
                                "function": {
                                    "arguments": function_arguments,
                                    "name": tool_name,
                                },
                            }
                        ],
                    }
                else:
                    new_entry = {"role": role, "content": safe_content}

            self.messages.append(new_entry)
            json.dumps(self.messages)

            return self.messages

        except Exception as e:
            raise ValueError(f"Failed to validate and append entry: {e}")

    def validate_entry(self, role, content):
        """
        Validates a single dictionary entry for JSON compliance.

        Args:
            role (str): The role to validate (e.g., "user", "developer").
            content (str): The content to validate.

        Returns:
            dict: A validated and JSON-compliant dictionary entry.

        Raises:
            ValueError: If validation fails for the entry.
        """
        try:
            if not isinstance(role, str):
                raise ValueError("Role must be a string.")
            if role.strip() == "":
                raise ValueError("Role cannot be an empty string.")

            if not isinstance(content, str):
                content = str(content)

            safe_content = json.dumps(content)[1:-1]

            return {"role": role, "content": safe_content}

        except Exception as e:
            raise ValueError(f"Failed to validate entry: {e}")

    def generateSysMessageForLLM(self, content: str):
        print(
            self.agent_name_identifier.capitalize(),
            ": ",
            "Currently LLM is openai? ",
            self.isOpenaiLLM,
        )
        if self.isOpenaiLLM:
            return self.validate_entry(role="system", content=content)
        else:
            return self.validate_entry(role="system", content=content)

    def refreshSysMessage(self, content: str = None):
        self.messages[0] = self.generateSysMessageForLLM(content=self.sys_prompt)

    def updateSysMessage(self, content: str = None):
        if not content:
            self.messages[0] = self.generateSysMessageForLLM(content=self.sys_prompt)
        else:
            self.sys_prompt = content
            self.sys_prompt_original = content
            self.messages[0] = self.generateSysMessageForLLM(content=content)

    def getSystemMessage(
        self,
    ):
        return self.sys_prompt

    def clearMessageHistory(self, del_systen_chat_history: bool = False):
        if self.logging:
            print(
                self.agent_name_identifier.capitalize(),
                ": ",
                f"Deleting chat history..🗑️ for {self.agent_name_identifier}",
            )
        self.messages.clear()
        if self.use_system_prompt_as_context and del_systen_chat_history:
            self.system_prompt_contexts_history = ""
            self.generate_system_prompt_with_context(context_string=None)
        self.appendToMessages(role="system", content=self.sys_prompt)
        if self.logging and self.deeper_logs:
            print(
                self.agent_name_identifier.capitalize(),
                ": ",
                "Agent chat history cleared 🧹: ",
                self.messages,
                "\n",
                color="magenta",
            )

    def trim_list1(self, input_list: list, count: int):
        """
        Trim the list to the last 'count' items if the length is greater than 'count'.

        Args:
            input_list (list): The input list to be trimmed.
            count (int): The desired count of items in the final list.

        Returns:
            list: Trimmed list.
        """
        print(self.agent_name_identifier.capitalize(), ": ", "trimmnig list")

        if len(input_list) < count:
            return input_list

        print(
            self.agent_name_identifier.capitalize(),
            ": ",
            f"last message item: {input_list[-1]}",
            color="yellow",
        )
        if input_list[-1].get("tool_calls", None):
            print(
                "skkipping trimmnig list since last message has tool_calls...",
                color="red",
            )

            return input_list

        else:
            if not self.use_system_prompt_as_context:
                input_list = input_list[-count:]
                input_list.insert(
                    0, self.generateSysMessageForLLM(content=self.sys_prompt)
                )
            else:
                input_list = input_list[-count:]
                input_list.insert(
                    0, self.generateSysMessageForLLM(content=self.sys_prompt)
                )
            return input_list

    def is_candidate_valid(self, candidate: list) -> bool:
        """
        Check that every message with role 'tool' is preceded by at least one message that contains a tool call.

        Args:
            candidate (list): List of messages to validate.

        Returns:
            bool: True if the candidate is valid, False otherwise.
        """
        for idx, msg in enumerate(candidate):
            if msg.get("role") == "tool":
                if idx == 0 or not any(m.get("tool_calls") for m in candidate[:idx]):
                    return False
        return True

    def trim_list(self, input_list: list, count: int):
        """
        Trim the conversation history to (at least) the last 'count' messages.

        Ensures that if any message includes a tool call (via "tool_calls")
        or is a tool response (role == "tool"), its counterpart is included.
        If extending is needed to maintain a valid pair sequence, the final
        message list might exceed the desired count.

        Args:
            input_list (list): The input list to be trimmed.
            count (int): The desired count of items in the final list.

        Returns:
            list: Trimmed list with proper tool call/response pairing.
        """
        print(
            f"{self.agent_name_identifier.capitalize()}: Trimming list", color="magenta"
        )

        if len(input_list) <= count:
            candidate = input_list[:]
        else:
            candidate_start = len(input_list) - count
            candidate = input_list[candidate_start:]

            while candidate_start > 0 and not self.is_candidate_valid(candidate):
                candidate_start -= 1
                candidate = input_list[candidate_start:]

        if len(candidate) > count:
            print(
                f"{self.agent_name_identifier.capitalize()}: Extended candidate length to preserve tool pairs (final count: {len(candidate)})"
            )

        candidate.insert(0, self.generateSysMessageForLLM(content=self.sys_prompt))
        return candidate

    def ava_main_executor(
        self, messages: List[dict], tools_list: List[BaseTool], ava_llm: LLM
    ):
        """
        Main orchestrator for agent execution with tool calling capabilities.

        This is the core execution engine that manages the interaction between the user,
        LLM, and available tools. It handles iteration limits, callbacks, and delegates
        to specific LLM handlers based on the provider type.

        Args:
            messages (List[dict]): List of conversation messages in the format:
                [{"role": "user/assistant/system", "content": "message text"}, ...]
            tools_list (List[BaseTool]): List of tool instances available for the agent:
                [MyTool(), AnotherTool(), ...]
            ava_llm (LLM): Language model instance for generating completions

        Returns:
            str or Any: The agent's response, which could be:
                - Direct text response from the LLM
                - Tool execution result (if tool returns direct)
                - Streaming response generator
                - Error message if max iterations exceeded

        Raises:
            ValueError: If invalid parameters are passed or max iterations exceeded
                       (when throw_error_on_iteration_exceed is True)

        Note:
            - Enforces maximum iteration limits to prevent infinite loops
            - Supports callback handlers for monitoring execution
            - Creates a copy of tools_list to prevent modification of original
            - Resets iteration counter on completion or error

        Example:
            >>> response = agent.ava_main_executor(messages, [search_tool, calc_tool], openai_llm)
        """
        # Create a copy to avoid modifying the original tools list
        tools_list_copy = tools_list.copy()

        # Check iteration limits to prevent infinite loops
        if self.current_agent_iteration <= self.max_agent_iterations:
            self.current_agent_iteration += 1

            # Log detailed information if debugging is enabled
            if self.logging:
                print(
                    self.agent_name_identifier.capitalize(),
                    ": ",
                    "Messages List: ",
                    self.messages,
                    "\n",
                    color="purple",
                )

            # Trigger callback if handler is configured
            if self.callback_handler and hasattr(self.callback_handler, "on_agent_run"):
                self.callback_handler.on_agent_run(input_msg="agent started running!")

            # Validate that we have messages and an LLM instance
            if self.messages and self.ava_llm:
                # Delegate to specific LLM handler
                if self.isOpenaiLLM:
                    return self.handle_openai_llm_completions(
                        messages=messages, tools_list=tools_list_copy, ava_llm=ava_llm
                    )
                else:
                    # Currently all LLM types use the same handler
                    return self.handle_openai_llm_completions(
                        messages=messages, tools_list=tools_list_copy, ava_llm=ava_llm
                    )

            # Reset iteration counter on successful completion
            self.current_agent_iteration = 0
            raise ValueError(
                f"Error: Check the passed message: {messages}, tools: {tools_list_copy}, and ava llm: {ava_llm}"
            )
        else:
            # Handle max iterations exceeded
            self.current_agent_iteration = 0
            if not self.throw_error_on_iteration_exceed:
                # Return a user-friendly error message
                return (
                    "Sorry! I wasn't able to complete your query after several tries!"
                )
            # Raise an exception for programmatic handling
            raise ValueError(
                f"{self.agent_name_identifier} wasn't able to come to a conclusion and exceeded "
                f"the max agent iteration count of {self.max_agent_iterations}"
            )

    def handle_openai_llm_completions(
        self, messages: List[dict], tools_list: List[BaseTool], ava_llm: OpenaiLLM
    ):
        llm_resp = None
        if not self.streaming:
            t0 = time.time()
            llm_resp = ava_llm.ava_llm_completions(
                self.messages,
                self.converted_tools_list,
                is_function_based=self.is_function_based,
                streaming=self.streaming,
                tool_choice=self.tool_choice,
            )
            if self.logging:
                t1 = time.time() - t0
                print(
                    self.agent_name_identifier.capitalize(),
                    ": ",
                    "AI responded in : {:.2f} milliseconds".format(t1 * 1000),
                    color="blue",
                )
                print(
                    self.agent_name_identifier.capitalize(),
                    ": ",
                    "OPENAI LLM RESP:",
                    llm_resp,
                    "\n",
                    color="green",
                )
            return self.complete_normal_openai_llm_response(
                llm_resp=llm_resp,
                messages=messages,
                tools_list=tools_list,
                ava_llm=ava_llm,
            )

        else:
            t0 = time.time()
            llm_resp = ava_llm.ava_llm_completions(
                self.messages,
                self.converted_tools_list,
                is_function_based=self.is_function_based,
                streaming=self.streaming,
                tool_choice=self.tool_choice,
            )
            if self.logging:
                t1 = time.time() - t0
                print(
                    self.agent_name_identifier.capitalize(),
                    ": ",
                    "AI responded in : {:.2f} milliseconds".format(t1 * 1000),
                )
                print(
                    self.agent_name_identifier.capitalize(),
                    ": ",
                    "OPENAI STREAMING LLM RESP:",
                    llm_resp,
                    "\n",
                    color="green",
                )
            return self.complete_streaming_openai_llm_response(
                llm_resp=llm_resp,
                messages=messages,
                tools_list=tools_list,
                ava_llm=ava_llm,
                start_time=t0,
            )

    def complete_normal_openai_llm_response(  # noqa: C901
        self,
        llm_resp,
        messages: List[dict],
        tools_list: List[BaseTool],
        ava_llm: OpenaiLLM,
    ):
        agent_response = llm_resp.choices[0].message
        if not self.is_function_based:
            if llm_resp.choices[0].message.tool_calls:
                """THIS MEANS AGENT MADE TOOL CALL"""

                if self.isOpenaiLLM:
                    messages.append(
                        {
                            "role": agent_response.role,
                            "content": "",
                            "tool_calls": [
                                tool_call.model_dump()
                                for tool_call in llm_resp.choices[0].message.tool_calls
                            ],
                        }
                    )
                if self.logging:
                    print(
                        self.agent_name_identifier.capitalize(),
                        ": ",
                        "Total tools called: ",
                        len(llm_resp.choices[0].message.tool_calls),
                    )
                for tool_call in llm_resp.choices[0].message.tool_calls:
                    name, params, tool_id = extract_function_info(
                        tool_call=tool_call, is_function_based=self.is_function_based
                    )

                    if name:
                        if self.logging:
                            print(
                                self.agent_name_identifier.capitalize(),
                                ": ",
                                f"Executing tool '{name}' ... with param(s): ",
                                f"'{params}'",
                                "\n",
                                color="yellow",
                            )
                        if self.callback_handler and hasattr(
                            self.callback_handler, "on_tool_call"
                        ):
                            self.callback_handler.on_tool_call(
                                tool_name=name, tool_params=params
                            )

                        if len(json.loads(params)) == 0:
                            print(
                                self.agent_name_identifier.capitalize(),
                                ": ",
                                "Empty param received!",
                                color="yellow",
                            )
                        resp, is_direct = find_and_execute_tool(
                            tool_name=name,
                            tool_params=json.loads(params),
                            tools_list=tools_list,
                            is_empty_tool_params=(
                                True if len(json.loads(params)) == 0 else False
                            ),
                        )

                        if resp:
                            if self.logging:
                                print(
                                    self.agent_name_identifier.capitalize(),
                                    ": ",
                                    f"Tool '{name}' response: ",
                                    resp,
                                    "\n",
                                    color="blue",
                                )

                            if self.isOpenaiLLM:
                                self.appendToMessages(
                                    role="tool",
                                    tool_name=name,
                                    content=resp,
                                    tool_call_id=tool_id,
                                )

                            if self.use_system_prompt_as_context:
                                self.system_prompt_contexts_history += (
                                    f"\nTOOL({name}): {resp}"
                                )
                            if is_direct:
                                if self.logging:
                                    print(
                                        self.agent_name_identifier.capitalize(),
                                        ": ",
                                        "Returning tool response as direct message",
                                        "\n",
                                        color="magenta",
                                    )
                                    print(
                                        f"{self.agent_name_identifier.capitalize()} message: ",
                                        resp,
                                        color="yellow",
                                    )
                                    print()

                                self.appendToMessages(role="assistant", content=resp)
                                if self.use_system_prompt_as_context:
                                    if not self.include_message_timestap:
                                        self.system_prompt_contexts_history += (
                                            f"\nYOU:{resp}"
                                        )
                                    else:
                                        self.system_prompt_contexts_history += f"\nYOU(SystemNote:{get_current_timestamp()}):{resp}"
                                    self.generate_system_prompt_with_context(
                                        context_string=self.system_prompt_contexts_history
                                    )
                                    self.updateSysMessage()
                                return resp

                return self.ava_main_executor(
                    messages=messages, tools_list=tools_list, ava_llm=ava_llm
                )

            else:
                """THIS MEANS THE AGENT JUST REPLIED NORMALLY WITHOUT FUNCTION OR TOOL CALLING"""
                agent_mes = llm_resp.choices[0].message.content
                self.appendToMessages(role="assistant", content=agent_mes)
                if self.use_system_prompt_as_context:
                    if not self.include_message_timestap:
                        self.system_prompt_contexts_history += f"\nYOU:{agent_mes}"
                    else:
                        self.system_prompt_contexts_history += (
                            f"\nYOU(SystemNote:{get_current_timestamp()}):{agent_mes}"
                        )
                    self.generate_system_prompt_with_context(
                        context_string=self.system_prompt_contexts_history
                    )
                    self.updateSysMessage()
                if self.logging:
                    print(
                        f"{self.agent_name_identifier.capitalize()} message: ",
                        agent_mes,
                        color="yellow",
                    )
                    print()
                if self.callback_handler and hasattr(
                    self.callback_handler, "on_general_response"
                ):
                    self.callback_handler.on_general_response(response=agent_mes)
                self.current_agent_iteration = 0
                if self.tts_streaming:
                    pass
                return agent_mes

        else:
            if llm_resp.choices[0].message.function_call:
                """THIS MEANS AGENT MADE FUNCTION CALL"""
                for _function_call in llm_resp.choices[0].message.function_call:
                    name, params, tool_id = extract_function_info(
                        tool_call=llm_resp.choices[0].message.function_call,
                        is_function_based=self.is_function_based,
                    )

                    if name:
                        if self.logging:
                            print(
                                self.agent_name_identifier.capitalize(),
                                ": ",
                                f"Executing function '{name}' ... with param(s): ",
                                f"'{params}'",
                                "\n",
                                color="yellow",
                            )
                        if self.callback_handler and hasattr(
                            self.callback_handler, "on_tool_call"
                        ):
                            self.callback_handler.on_tool_call(
                                tool_name=name, tool_params=params
                            )

                        resp, is_direct = find_and_execute_tool(
                            tool_name=name,
                            tool_params=json.loads(params),
                            tools_list=tools_list,
                        )

                        if resp:
                            if self.logging:
                                print(
                                    self.agent_name_identifier.capitalize(),
                                    ": ",
                                    f"Returned From Function '{name}' response: ",
                                    resp,
                                    "\n",
                                    color="blue",
                                )

                            messages.append(
                                {
                                    "role": "function",
                                    "name": name,
                                    "content": resp,
                                }
                            )
                            if self.use_system_prompt_as_context:
                                self.system_prompt_contexts_history += (
                                    f"\nFUNCTION({name}): {resp}"
                                )

                            if is_direct:
                                print(
                                    self.agent_name_identifier.capitalize(),
                                    ": ",
                                    "Returning tool response as direct message",
                                    "\n",
                                    color="magenta",
                                )
                                self.appendToMessages(role="assistant", content=resp)
                                if self.use_system_prompt_as_context:
                                    if not self.include_message_timestap:
                                        self.system_prompt_contexts_history += (
                                            f"\nYOU:{resp}"
                                        )
                                    else:
                                        self.system_prompt_contexts_history += f"\nYOU(SystemNote:{get_current_timestamp()}):{resp}"
                                    self.generate_system_prompt_with_context(
                                        context_string=self.system_prompt_contexts_history
                                    )
                                    self.updateSysMessage()
                                return resp
                return self.ava_main_executor(
                    messages=messages, tools_list=tools_list, ava_llm=ava_llm
                )

            else:
                """THIS MEANS THE AGENT JUST REPLIED NORMALLY WITHOUT FUNCTION OR TOOL CALLING"""

                agent_mes = llm_resp.choices[0].message.content
                self.appendToMessages(role="assistant", content=agent_mes)
                if self.use_system_prompt_as_context:
                    if not self.include_message_timestap:
                        self.system_prompt_contexts_history += f"\nYOU:{agent_mes}"
                    else:
                        self.system_prompt_contexts_history += (
                            f"\nYOU(SystemNote:{get_current_timestamp()}):{agent_mes}"
                        )
                    self.generate_system_prompt_with_context(
                        context_string=self.system_prompt_contexts_history
                    )
                    self.updateSysMessage()

                if self.logging:
                    print(
                        f"{self.agent_name_identifier.capitalize()} message: ",
                        agent_mes,
                        color="yellow",
                    )
                    print()
                if self.callback_handler and hasattr(
                    self.callback_handler, "on_general_response"
                ):
                    self.callback_handler.on_general_response(response=agent_mes)
                self.current_agent_iteration = 0
                print(
                    self.agent_name_identifier.capitalize(),
                    ": ",
                    "TTS STREAMING VAL:",
                    self.tts_streaming,
                )
                if self.tts_streaming:
                    pass
                return agent_mes

    def complete_streaming_openai_llm_response(  # noqa: C901
        self,
        llm_resp,
        messages: List[dict],
        tools_list: List[BaseTool],
        ava_llm: OpenaiLLM,
        start_time: float,
    ):
        response_text: str = ""
        previous_chunk = ""
        stop_reason = None
        function_chunk = None
        tts_chunk: str = ""
        function_response = {
            "name": "",
            "arguments": "",
            "id": "",
            "tool_call_model_dump": {},
        }
        is_function_call = False

        first_token_received = False

        for line in llm_resp:
            if not first_token_received:
                first_token_received = True
                elapsed = time.time() - start_time
                print(f"\nTime to first token: {elapsed:.3f} seconds\n", color="blue")

            if self.logging:
                print(
                    self.agent_name_identifier.capitalize(),
                    ": ",
                    "Openai LLM streaming line: ",
                    line,
                    line,
                    color="green",
                )
                print()
            chunk = None

            if len(line.choices) < 1:
                continue

            if line.choices[0].finish_reason:
                print("", end="\n", flush=True)
                stop_reason = line.choices[0].finish_reason
                if self.logging:
                    print(
                        self.agent_name_identifier.capitalize(),
                        ": ",
                        "Steams ends with reason: ",
                        stop_reason,
                        "\nFUNCTION CALL: ",
                        is_function_call,
                    )
                break
            if line.choices[0].delta:
                chunk = line.choices[0].delta.content
                function_chunk = line.choices[0].delta.tool_calls
            if function_chunk:
                is_function_call = True
                for tool_call in function_chunk:
                    function_info = tool_call.function

                    if tool_call.id:
                        function_response["id"] += tool_call.id
                    if tool_call.model_dump().get("id", None):
                        function_response["tool_call_model_dump"].update(
                            tool_call.model_dump()
                        )
                    if function_info.name:
                        function_response["name"] += function_info.name
                        function_response["tool_call_model_dump"]["function"][
                            "name"
                        ] = (function_response["name"] + function_info.name)

                    if function_info.arguments:
                        function_response["arguments"] += function_info.arguments
                        function_response["tool_call_model_dump"]["function"][
                            "arguments"
                        ] = (function_response["arguments"] + function_info.arguments)

                print(
                    f"{self.agent_name_identifier.capitalize()} Tool call : ",
                    function_response,
                    color="yellow",
                    end="\r",
                    flush=True,
                )

            elif chunk and chunk != previous_chunk and function_chunk is None:
                is_function_call = False
                response_text += chunk
                tts_chunk += chunk
                if self.callback_handler and hasattr(
                    self.callback_handler, "on_streaming_chunk"
                ):
                    self.callback_handler.on_streaming_chunk(chunk=chunk)

                if self.print_tts_streaming:
                    print(
                        f"{self.agent_name_identifier.capitalize()} message: ",
                        response_text,
                        color="yellow",
                        end="\r",
                        flush=True,
                    )
                previous_chunk = chunk
                if tts_chunk.strip()[-1] in {
                    ".",
                    "!",
                    "?",
                }:
                    if self.tts_streaming:
                        tts_chunk = ""

        print("", end="\n", flush=True)
        if not is_function_call:
            agent_mes = response_text
            self.appendToMessages(role="assistant", content=agent_mes)
            if self.use_system_prompt_as_context:
                if not self.include_message_timestap:
                    self.system_prompt_contexts_history += f"\nYOU:{agent_mes}"
                else:
                    self.system_prompt_contexts_history += (
                        f"\nYOU(SystemNote:{get_current_timestamp()}):{agent_mes}"
                    )
                self.generate_system_prompt_with_context(
                    context_string=self.system_prompt_contexts_history
                )
                self.updateSysMessage()

            if self.callback_handler and hasattr(
                self.callback_handler, "on_general_response"
            ):
                self.callback_handler.on_general_response(response=agent_mes)
            self.current_agent_iteration = 0
            return agent_mes

        else:
            """This means there is streaming function or say tool call fuckkkkkkkkk"""

            if function_response:
                name = function_response["name"]
                params = function_response["arguments"]
                id = function_response["id"]
                tool_call_dump = function_response["tool_call_model_dump"]
                tool_call_dump["function"]["name"] = name

                print(f"tool call model dump:{tool_call_dump} ")
                messages.append(
                    {"role": "assistant", "content": "", "tool_calls": [tool_call_dump]}
                )
                if name:
                    if self.logging:
                        print(
                            self.agent_name_identifier.capitalize(),
                            ": ",
                            f"Executing tool '{name}' ... with param(s): ",
                            f"'{params}'",
                            "\n",
                            color="yellow",
                        )
                    if self.callback_handler and hasattr(
                        self.callback_handler, "on_tool_call"
                    ):
                        self.callback_handler.on_tool_call(
                            tool_name=name, tool_params=params
                        )

                    resp, is_direct = find_and_execute_tool(
                        tool_name=name,
                        tool_params=json.loads(params),
                        tools_list=tools_list,
                    )

                    if resp:
                        if self.logging:
                            print(
                                self.agent_name_identifier.capitalize(),
                                ": ",
                                f"Tool '{name}' response: ",
                                resp,
                                "\n",
                                color="blue",
                            )

                        if self.isOpenaiLLM:
                            messages.append(
                                {
                                    "tool_call_id": id,
                                    "role": "tool",
                                    "name": name,
                                    "content": resp,
                                }
                            )
                        else:
                            messages.append(
                                {
                                    "tool_call_id": id,
                                    "role": "tool",
                                    "name": name,
                                    "content": resp,
                                }
                            )
                        if self.use_system_prompt_as_context:
                            self.system_prompt_contexts_history += (
                                f"\nTOOL({name}): {resp}"
                            )

                        if is_direct:
                            if self.logging:
                                print(
                                    self.agent_name_identifier.capitalize(),
                                    ": ",
                                    "Returning tool response as direct message",
                                    "\n",
                                    color="magenta",
                                )
                                print(
                                    self.agent_name_identifier,
                                    ": ",
                                    f"{self.agent_name_identifier.capitalize()} message: ",
                                    resp,
                                    color="yellow",
                                )
                                print()

                            self.appendToMessages(role="assistant", content=resp)
                            if self.use_system_prompt_as_context:
                                if not self.include_message_timestap:
                                    self.system_prompt_contexts_history += (
                                        f"\nYOU:{resp}"
                                    )
                                else:
                                    self.system_prompt_contexts_history += f"\nYOU(SystemNote:{get_current_timestamp()}):{resp}"
                                self.generate_system_prompt_with_context(
                                    context_string=self.system_prompt_contexts_history
                                )
                                self.updateSysMessage()
                            return resp
            return self.ava_main_executor(
                messages=messages, tools_list=tools_list, ava_llm=ava_llm
            )

    def prepare_conversation_history_summary(
        self,
    ):
        """This function is for preparing and conversation summary from the prior messages."""
        pass

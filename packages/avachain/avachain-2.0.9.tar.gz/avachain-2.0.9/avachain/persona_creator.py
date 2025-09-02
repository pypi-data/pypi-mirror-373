"""
Avachain Persona Creator - AI agent persona management system.

This module provides comprehensive tools for creating, managing, and deploying
AI agent personas. It includes functionality for converting tools to JSON format,
uploading assets, and integrating with persona management APIs.
"""

import inspect
import json
import os
import textwrap
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Type, Union

import requests
from print_color import print
from pydantic_core import PydanticUndefined

from .avachain import BaseTool
from .avachain_executor import AvaAgent

# API Configuration Constants
API_BASE_URL = "https://avaai.pathor.in/api/v1"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/users/userStorage/storeicon/"
CREATE_PERSONA_ENDPOINT = f"{API_BASE_URL}/persona/createPersona"
UPDATE_PERSONA_ENDPOINT = f"{API_BASE_URL}/persona/updatePersona"
DELTET_PERSONA_ENDPOINT = f"{API_BASE_URL}/persona/deletePersona/dummyy/"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


@dataclass
class TypeMapping:
    """
    Type mapping utility for converting Python types to JSON schema types.

    This class provides a centralized mapping system for converting Python
    built-in types to their corresponding JSON schema representations.
    """

    TYPES = {
        int: "number",
        float: "number",
        str: "string",
        bool: "boolean",
    }

    @classmethod
    def to_json_type(cls, type_info: Type) -> str:
        """
        Convert Python type to JSON schema type string.

        Args:
            type_info (Type): Python type object to convert

        Returns:
            str: JSON schema type string

        Example:
            >>> TypeMapping.to_json_type(int)
            'number'
        """
        return cls.TYPES.get(type_info, str(type_info))


def validate_logo_path(logo_path: Union[str, Path]) -> Path:
    """
    Validate and normalize a logo file path.

    This function performs comprehensive validation of logo file paths,
    checking for existence, readability, and supported file formats.

    Args:
        logo_path (Union[str, Path]): Path to the logo file

    Returns:
        Path: Validated Path object

    Raises:
        ValueError: If path is invalid, file doesn't exist, or format unsupported

    Example:
        >>> path = validate_logo_path("assets/logo.png")
        >>> # Returns: Path("assets/logo.png") if valid
    """
    if not logo_path:
        raise ValueError("Logo path cannot be empty")

    path = Path(logo_path)

    if not path.exists():
        raise ValueError(f"Logo file does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Logo path is not a file: {path}")

    if path.suffix.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Logo file must be one of: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}. "
            f"Got: {path.suffix}"
        )

    if not os.access(path, os.R_OK):
        raise ValueError(f"Logo file is not readable: {path}")

    return path


def upload_file(file_path: Union[str, Path], token: str) -> str:
    """
    Upload a file to the server and return its URL.

    This function handles secure file upload to the Avachain storage system.
    It validates the file path, performs the upload with authentication,
    and returns the public URL of the uploaded file.

    Args:
        file_path (Union[str, Path]): Path to the file to upload
        token (str): Authentication Bearer token

    Returns:
        str: Public URL of the uploaded file

    Raises:
        Exception: If file validation fails or upload encounters an error

    Example:
        >>> url = upload_file("logo.png", "your_auth_token")
        >>> # Returns: "https://storage.example.com/uploads/logo.png"
    """
    try:
        # Validate the file path and format
        path = validate_logo_path(file_path)

        # Upload the file with authentication
        with open(path, "rb") as file:
            response = requests.post(
                UPLOAD_ENDPOINT,
                files={"file": file},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,  # 30 second timeout for file uploads
            )
            response.raise_for_status()
            return response.json()["location"]
    except Exception as e:
        print(f"Error uploading file: {e}")
        traceback.print_exc()
        raise


def convert_tool_to_json(tool: BaseTool, tool_id: str) -> Dict[str, Any]:
    """
    Convert a BaseTool object into a JSON representation for persona systems.

    This function transforms a BaseTool instance into a structured JSON format
    suitable for persona management systems. It extracts tool metadata,
    source code, and parameter schemas to create a complete tool specification.

    Args:
        tool (BaseTool): The tool object to convert
        tool_id (str): Unique identifier for the tool

    Returns:
        Dict[str, Any]: JSON representation containing tool metadata and schema

    Example:
        >>> tool = MyTool(name="search", description="Web search tool")
        >>> json_data = convert_tool_to_json(tool, "search_tool_v1")
    """
    # Extract and format the tool's source code
    run_method_source = textwrap.dedent(inspect.getsource(tool._run))

    # Create the base tool JSON structure
    tool_json = {
        "title": tool_id,
        "ai_description": tool.description,
        "func_run": run_method_source,
        "func_schema": {},
        "parameters": {
            "tool_extras": {
                "isDirect": tool.return_direct,
                "name": tool.name,
            },
            "tool_parameters": {},
        },
    }

    # Return early if no argument schema is defined
    if not tool.args_schema:
        return tool_json

    # Process tool parameters from the argument schema
    for field_name, field_info in tool.args_schema.__annotations__.items():
        field = tool.args_schema.model_fields[field_name]

        # Create field properties for JSON schema
        field_properties = {
            "type": TypeMapping.to_json_type(field_info),
            "description": getattr(field, "description", "No description available"),
            "default": "" if field.default is PydanticUndefined else field.default,
            "enum": [],
        }

        # Handle enum values if present in the field's extra data
        if field.json_schema_extra:
            enum_values = field.json_schema_extra.get("enumerate")
            if enum_values:
                field_properties["enum"] = enum_values

        # Add the field to the tool's parameter schema
        tool_json["parameters"]["tool_parameters"][field_name] = field_properties

    return tool_json


def prepare_tools_config(agent: AvaAgent) -> Dict[str, Any]:
    """
    Prepare tools configuration for an agent.

    This function extracts and formats the tools configuration from an AvaAgent
    instance, preparing it for persona creation or updates. It includes the
    base system prompt and converts all tools to JSON format.

    Args:
        agent (AvaAgent): The AvaAgent object containing tools and configuration

    Returns:
        Dict[str, Any]: Dictionary containing the tools configuration with:
            - base_sys_prompt: The original system prompt
            - tools: List of tools converted to JSON format

    Example:
        >>> agent = AvaAgent(sys_prompt="You are helpful", ava_llm=llm, tools_list=[tool1, tool2])
        >>> config = prepare_tools_config(agent)
    """
    try:
        config = {
            "base_sys_prompt": agent.sys_prompt_original,
            "tools": [
                convert_tool_to_json(tool, tool.name.lower())
                for tool in agent.tools_list
            ],
        }
        return config
    except Exception as e:
        print(f"Error preparing tools config: {e}")
        traceback.print_exc()
        return {}


def push_to_store(  # noqa: C901
    token: str,
    name: str,
    age: str,
    gender: str,
    public_description: str,
    logo_path: str,
    title: str = "",
    agent_obj: AvaAgent = None,
    can_be_used_as_tool: bool = False,
    behaviour: List[str] = None,
    tags: List[str] = None,
    languages: List[str] = None,
    hobbies: List[str] = None,
    supported_os: List[str] = None,
    is_public: bool = True,
    action: str = "create",
    custom_personaId: str = None,
    is_AssistantProfile: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """
    Push a persona to the AvA store as either an Agent or Assistant Profile.

    This function handles the complete workflow of creating, updating, or deleting
    personas in the AvA store. It supports both agent personas (with tools) and
    assistant profiles (without tools), with comprehensive validation and error handling.

    Args:
        token (str): Authentication Bearer token for API access
        name (str): Display name of the persona
        age (str): Age of the persona
        gender (str): Gender of the persona (affects voice selection)
        public_description (str): Public description/personality of the persona
        logo_path (str): File path to the persona's logo/avatar image
        title (str, optional): Optional title for the persona
        agent_obj (AvaAgent, optional): AvaAgent instance containing tools and configuration
        can_be_used_as_tool (bool): Whether this persona can be used as a tool by other agents
        behaviour (List[str], optional): List of behavioral traits
        tags (List[str], optional): List of tags for categorization
        languages (List[str], optional): List of supported languages
        hobbies (List[str], optional): List of persona's hobbies/interests
        supported_os (List[str], optional): List of supported operating systems
        is_public (bool): Whether the persona should be publicly accessible
        action (str): Action to perform - "create", "update", or "delete"
        custom_personaId (str, optional): Custom ID for the persona (required for update/delete)
        is_AssistantProfile (bool): Whether this is an assistant profile (no tools allowed)
        **kwargs: Additional keyword arguments for backward compatibility

    Returns:
        Dict[str, Any]: Server response containing operation results

    Raises:
        ValueError: If validation fails (e.g., missing required fields, invalid combinations)
        requests.exceptions.RequestException: If API request fails

    Example:
        >>> response = push_to_store(
        ...     token="your_token",
        ...     name="Assistant Bot",
        ...     age="25",
        ...     gender="female",
        ...     public_description="Helpful assistant",
        ...     logo_path="./avatar.png",
        ...     agent_obj=my_agent
        ... )
    """
    # Handle delete action with minimal validation
    if action == "delete":
        if not custom_personaId:
            raise ValueError("custom_personaId is required for delete operations")

        headers = {"Authorization": f"Bearer {token}"}
        url = DELTET_PERSONA_ENDPOINT + custom_personaId

        try:
            response = requests.delete(url=url, headers=headers, timeout=10)

            if not response.ok:
                error_detail = (
                    response.json()
                    if response.content
                    else "No error details available"
                )
                print(f"Server returned error: {error_detail}")

            response.raise_for_status()
            print(f"Successfully deleted persona with ID: {custom_personaId}")
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"\nError deleting persona: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                try:
                    error_detail = e.response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except ValueError:
                    print(f"Raw response: {e.response.text}")
            traceback.print_exc()
            raise

    # Handle backward compatibility for deprecated parameter names
    if "is_MainAssistant" in kwargs:
        is_AssistantProfile = kwargs["is_MainAssistant"]
        print(
            "Warning: 'is_MainAssistant' is deprecated. Use 'is_AssistantProfile' instead"
        )

    # Validate input combinations
    if is_AssistantProfile and agent_obj and agent_obj.tools_list:
        raise ValueError(
            "Assistant profiles cannot have tools. Remove tools or set is_AssistantProfile=False"
        )

    # Handle default supported OS based on persona type
    supported_os = supported_os or []
    if is_AssistantProfile:
        # Assistant profiles typically support the current OS
        supported_os.append("nt")
    elif not supported_os:
        # Agents must explicitly specify supported platforms
        raise ValueError(
            "Agents must support at least one OS. Specify 'nt' for Windows or 'android' for Android"
        )

    # Upload the persona's logo/avatar and get the public URL
    try:
        logo_url = upload_file(logo_path, token)
    except Exception as e:
        raise ValueError(f"Failed to upload logo: {e}")

    # Configure voice based on gender (used for TTS features)
    VOICE_ID = None
    if gender.lower() == "female":
        VOICE_ID = "682f215a4bb9c6314e454a3b"  # Female voice ID
    elif gender.lower() == "male":
        VOICE_ID = "682f21824bb9c6314e454a4c"  # Male voice ID

    # Prepare the request payload
    payload = {
        "name": name,
        "title": title,
        "age": age,
        "gender": gender,
        "languages": languages or [],
        "personality": public_description,
        "behavior": behaviour or [],
        "logo": logo_url,
        "voice": VOICE_ID,
        "os": supported_os,
        "hobbies": hobbies or [],
        "price": "nill",  # Currently all personas are free
        "tags": tags or [],
        "base_sys_prompt": "nil",  # Handled via tools_config
        "Is_main_agent": is_AssistantProfile,
        "is_agentic_tool": can_be_used_as_tool,
        "tools_config": prepare_tools_config(agent_obj) if agent_obj else {},
        "isPublic": is_public,
    }

    # Handle persona ID for different operations
    print("custom_persona_id:", custom_personaId)
    if action == "update":
        if not custom_personaId:
            raise ValueError("custom_personaId is required for update operations")
        payload["personaId"] = custom_personaId
    else:  # create action
        if custom_personaId:
            payload["customPersonaId"] = custom_personaId

    # Configure request parameters based on action
    url = UPDATE_PERSONA_ENDPOINT if action == "update" else CREATE_PERSONA_ENDPOINT
    method = "PUT" if action == "update" else "POST"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Make the API request
        response = requests.request(
            method, url=url, json=payload, headers=headers, timeout=10
        )

        # Handle non-success status codes
        if not response.ok:
            error_detail = (
                response.json() if response.content else "No error details available"
            )
            print(f"Server returned error: {error_detail}")

        response.raise_for_status()

        # Success response handling
        result = response.json()
        print(f"Status: {result.get('message', 'Operation completed successfully')}")
        return result

    except requests.exceptions.RequestException as e:
        print(f"\nError pushing to store: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                error_detail = e.response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except ValueError:
                print(f"Raw response: {e.response.text}")
        traceback.print_exc()
        raise

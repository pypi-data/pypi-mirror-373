"""
Avachain Tool Creator - Tool management and conversion utilities.

This module provides utilities for creating, converting, and managing AI agent tools.
It includes functions for converting BaseTool objects to JSON format compatible with
various AI platforms and APIs, as well as plugin server integration capabilities.
"""

import inspect
import json
import os
import textwrap
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from print_color import print
from pydantic_core import PydanticUndefined

from .avachain import BaseTool

# API Configuration Constants
API_BASE_URL = "https://avaai.pathor.in/api/v1"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/users/userStorage/storeicon/"
CREATE_PLUGIN_ENDPOINT = f"{API_BASE_URL}/plugin/createGlobalPlugin"
UPDATE_PLUGIN_ENDPOINT = f"{API_BASE_URL}/plugin/updateGlobalPlugin"
DELETE_PLUGIN_ENDPOINT = f"{API_BASE_URL}/plugin/deleteGlobalPlugin"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


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


def map_type_to_json(type_info):
    """
    Map Python types to JSON schema type strings.

    This function converts Python built-in types to their corresponding
    JSON schema type representations for API compatibility.

    Args:
        type_info: Python type object (int, float, str, bool, etc.)

    Returns:
        str: JSON schema type string ("number", "string", "boolean", etc.)

    Example:
        >>> map_type_to_json(int)
        'number'
        >>> map_type_to_json(str)
        'string'
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
    tool_id: str,
    human_description: str,
    public_name: str,
    logo_url: str = None,
    isAnonymous: bool = False,
    authentication_required: Optional[bool] = False,
    connection_url: Optional[str] = "",
    isAuthenticated: bool = False,
    isPublic: bool = True,
    isMain: bool = False,
    tags: Optional[List[str]] = None,
    supports_android: bool = False,
    supports_windows: bool = True,
) -> Dict[str, Any]:
    """
    Convert a BaseTool object into a comprehensive JSON representation for plugin systems.

    This function transforms a BaseTool instance into a detailed JSON schema format
    suitable for plugin marketplaces and tool registries. It extracts the tool's
    source code, metadata, and parameter schema to create a complete tool specification.

    Note: This is an internal function. Use makePluginServerRequest() for the public API.

    Args:
        tool (BaseTool): The tool object to convert
        tool_id (str): Unique identifier for the tool in the plugin system
        human_description (str): Human-readable description for end users
        public_name (str): Display name for the tool
        logo_url (str, optional): URL to the tool's logo/icon (should be uploaded already)
        isAnonymous (bool): Whether the tool can be used anonymously
        authentication_required (bool): Whether authentication is required
        connection_url (str): URL for establishing connections if needed
        isAuthenticated (bool): Current authentication status
        isPublic (bool): Whether the tool is publicly available
        isMain (bool): Whether this is the main/primary tool
        tags (List[str]): List of tags for categorization
        supports_android (bool): Android platform support
        supports_windows (bool): Windows platform support

    Returns:
        Dict[str, Any]: Comprehensive JSON representation of the tool

    Raises:
        ValueError: If neither android nor windows support is specified
    """
    # Extract the source code of the tool's _run method for inspection/execution
    run_method_source = inspect.getsource(tool._run)
    run_method_source = textwrap.dedent(run_method_source)
    print(run_method_source)

    # Validate platform support - at least one platform must be supported
    if not supports_android and not supports_windows:
        raise ValueError(
            "You must specify at least one of 'android', 'windows' as the os"
        )

    # Build supported OS list
    os_support = []
    if supports_windows:
        os_support.append(os.name)
    if supports_android:
        os_support = ["android"]

    # Create the comprehensive JSON representation
    json_representation = {
        "title": tool_id,
        "os": os_support,
        "human_description": human_description,
        "name": public_name,
        "ai_description": tool.description,
        "logo": logo_url,
        "isAnonymous": isAnonymous,
        "authentication_required": authentication_required,
        "connection_url": connection_url,
        "isAuthenticated": isAuthenticated,
        "isPublic": isPublic,
        "tags": tags if tags is not None else [],
        "func_run": run_method_source,
        "func_schema": {},
        "parameters": {
            "tool_extras": {
                "isMain": isMain,
                "isDirect": tool.return_direct,
                "name": tool.name,
            },
            "tool_parameters": {},
        },
    }

    # Build required arguments list and parameter schema
    required_args = []

    if tool.args_schema:
        # Process each field in the tool's argument schema
        for field_name, field_info in tool.args_schema.__annotations__.items():
            # Get field description from the Pydantic model field
            field_description = getattr(
                tool.args_schema.model_fields[field_name],
                "description",
                "No description available",
            )

            # Create field properties for JSON schema
            field_properties = {
                "type": map_type_to_json(field_info),
                "description": field_description,
            }

            # Check if field is required (repr=True in Pydantic)
            if tool.args_schema.model_fields[field_name].repr:
                required_args.append(str(field_name))

            # Handle default values
            default_value = tool.args_schema.model_fields[field_name].default
            field_properties["default"] = ""
            if default_value is not None and default_value is not PydanticUndefined:
                field_properties["default"] = default_value

            # Handle enum values if present
            enums_present = tool.args_schema.model_fields[field_name].json_schema_extra
            field_properties["enum"] = []
            if enums_present:
                enum_values = enums_present.get("enumerate", None)
                if enum_values is not None:
                    field_properties["enum"] = enum_values

            # Add field to the parameters schema
            json_representation["parameters"]["tool_parameters"][
                field_name
            ] = field_properties

    return json_representation


def _handle_logo_upload(logo: str, token: str) -> Optional[str]:
    """
    Handle logo upload if it's a file path, otherwise return the URL as-is.

    Args:
        logo (str): Logo URL or file path
        token (str): Authentication token

    Returns:
        Optional[str]: Logo URL or None
    """
    if not logo:
        return None

    # Check if logo is a file path vs URL
    if (
        not logo.startswith(("http://", "https://"))
        and Path(logo).suffix.lower() in ALLOWED_IMAGE_EXTENSIONS
    ):
        try:
            print(f"Uploading logo file: {logo}")
            logo_url = upload_file(logo, token)
            print(f"Logo uploaded successfully: {logo_url}")
            return logo_url
        except Exception as e:
            raise ValueError(f"Failed to upload logo: {e}")

    return logo


def _validate_create_update_params(
    tool: BaseTool, human_description: str, public_name: str
):
    """
    Validate required parameters for create/update actions.

    Args:
        tool (BaseTool): The tool object
        human_description (str): Human description
        public_name (str): Public name

    Raises:
        ValueError: If validation fails
    """
    if not tool:
        raise ValueError("Tool object is required for create/update actions")
    if not human_description:
        raise ValueError("Human description is required for create/update actions")
    if not public_name:
        raise ValueError("Public name is required for create/update actions")


def _make_api_request(
    method: str, url: str, payload: Dict[str, Any], token: str, timeout: int = 10
) -> Dict[str, Any]:
    """
    Make an API request with proper error handling.

    Args:
        method (str): HTTP method
        url (str): Request URL
        payload (Dict[str, Any]): Request payload
        token (str): Authentication token
        timeout (int): Request timeout in seconds

    Returns:
        Dict[str, Any]: Response data

    Raises:
        requests.exceptions.RequestException: If request fails
    """
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    try:
        response = requests.request(
            method, url, headers=headers, data=json.dumps(payload), timeout=timeout
        )

        if not response.ok:
            error_detail = (
                response.json() if response.content else "No error details available"
            )
            print(f"Server returned error: {error_detail}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"\nAPI request error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            try:
                error_detail = e.response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except ValueError:
                print(f"Raw response: {e.response.text}")
        traceback.print_exc()
        raise


def _delete_tool_plugin(tool_id: str, token: str) -> Dict[str, Any]:
    """
    Delete a tool plugin.

    Args:
        tool_id (str): Tool ID to delete
        token (str): Authentication token

    Returns:
        Dict[str, Any]: Response data
    """
    payload = {"title": tool_id}
    result = _make_api_request("DELETE", DELETE_PLUGIN_ENDPOINT, payload, token)
    print(f"Successfully deleted tool plugin: {tool_id}")
    return result


def _create_or_update_tool_plugin(
    action: str,
    token: str,
    tool: BaseTool,
    tool_id: str,
    human_description: str,
    public_name: str,
    logo: str = None,
    isAnonymous: bool = False,
    authentication_required: Optional[bool] = False,
    connection_url: Optional[str] = "",
    isAuthenticated: bool = False,
    isPublic: bool = True,
    isMain: bool = False,
    tags: Optional[List[str]] = None,
    supports_android: bool = False,
    supports_windows: bool = True,
) -> Dict[str, Any]:
    """
    Create or update a tool plugin.

    Args:
        action (str): "create" or "update"
        token (str): Authentication token
        tool (BaseTool): Tool object
        tool_id (str): Tool ID
        human_description (str): Human description
        public_name (str): Public name
        logo (str): Logo URL or file path
        ... (other parameters as per convert_tool_to_json)

    Returns:
        Dict[str, Any]: Response data
    """
    # Validate parameters
    _validate_create_update_params(tool, human_description, public_name)

    # Handle logo upload
    logo_url = _handle_logo_upload(logo, token)

    # Convert tool to JSON
    try:
        tool_json = convert_tool_to_json(
            tool=tool,
            tool_id=tool_id,
            human_description=human_description,
            public_name=public_name,
            logo_url=logo_url,
            isAnonymous=isAnonymous,
            authentication_required=authentication_required,
            connection_url=connection_url,
            isAuthenticated=isAuthenticated,
            isPublic=isPublic,
            isMain=isMain,
            tags=tags,
            supports_android=supports_android,
            supports_windows=supports_windows,
        )
    except Exception as e:
        print(f"Error converting tool to JSON: {e}")
        traceback.print_exc()
        raise

    # Configure URL based on action
    url = UPDATE_PLUGIN_ENDPOINT if action == "update" else CREATE_PLUGIN_ENDPOINT
    method = "PUT" if action == "update" else "POST"

    # Make API request
    result = _make_api_request(method, url, tool_json, token, timeout=30)

    # Success message
    action_msg = "created" if action == "create" else "updated"
    print(f"Tool plugin {action_msg} successfully: {tool_id}")
    print(f"Status: {result.get('message', f'Tool {action_msg} successfully')}")

    return result


def makePluginServerRequest(
    action: str,
    token: str,
    tool_id: str,
    tool: BaseTool = None,
    human_description: str = None,
    public_name: str = None,
    logo: str = None,
    isAnonymous: bool = False,
    authentication_required: Optional[bool] = False,
    connection_url: Optional[str] = "",
    isAuthenticated: bool = False,
    isPublic: bool = True,
    isMain: bool = False,
    tags: Optional[List[str]] = None,
    supports_android: bool = False,
    supports_windows: bool = True,
) -> Dict[str, Any]:
    """
    Create, update, or delete a tool plugin on the Avachain plugin server.

    This function provides a unified interface for managing tool plugins. It handles
    logo upload, tool conversion to JSON format, and API communication with proper
    error handling and validation.

    Args:
        action (str): Type of action - "create", "update", or "delete"
        token (str): Authentication Bearer token for API access
        tool_id (str): Unique identifier for the tool in the plugin system
        tool (BaseTool, optional): The tool object to convert (not needed for delete)
        human_description (str, optional): Human-readable description (not needed for delete)
        public_name (str, optional): Display name for the tool (not needed for delete)
        logo (str, optional): URL or file path to the tool's logo/icon
        isAnonymous (bool): Whether the tool can be used anonymously
        authentication_required (bool): Whether authentication is required
        connection_url (str): URL for establishing connections if needed
        isAuthenticated (bool): Current authentication status
        isPublic (bool): Whether the tool is publicly available
        isMain (bool): Whether this is the main/primary tool
        tags (List[str]): List of tags for categorization
        supports_android (bool): Android platform support
        supports_windows (bool): Windows platform support

    Returns:
        Dict[str, Any]: Server response containing operation results

    Raises:
        ValueError: If validation fails or required parameters are missing
        requests.exceptions.RequestException: If API request fails

    Example:
        >>> # Create a new tool plugin
        >>> response = makePluginServerRequest(
        ...     action="create",
        ...     token="your_auth_token",
        ...     tool_id="web_search_v1",
        ...     tool=my_search_tool,
        ...     human_description="Search the web for information",
        ...     public_name="Web Search",
        ...     logo="./search_icon.png",
        ...     tags=["search", "web", "information"]
        ... )

        >>> # Update an existing tool
        >>> response = makePluginServerRequest(
        ...     action="update",
        ...     token="your_auth_token",
        ...     tool_id="web_search_v1",
        ...     tool=updated_search_tool,
        ...     human_description="Enhanced web search tool",
        ...     public_name="Enhanced Web Search"
        ... )

        >>> # Delete a tool
        >>> response = makePluginServerRequest(
        ...     action="delete",
        ...     token="your_auth_token",
        ...     tool_id="web_search_v1"
        ... )
    """
    if action == "delete":
        return _delete_tool_plugin(tool_id, token)

    return _create_or_update_tool_plugin(
        action=action,
        token=token,
        tool=tool,
        tool_id=tool_id,
        human_description=human_description,
        public_name=public_name,
        logo=logo,
        isAnonymous=isAnonymous,
        authentication_required=authentication_required,
        connection_url=connection_url,
        isAuthenticated=isAuthenticated,
        isPublic=isPublic,
        isMain=isMain,
        tags=tags,
        supports_android=supports_android,
        supports_windows=supports_windows,
    )

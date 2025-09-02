# Import all public classes and functions from core

__version__ = "2.0.8"
__author__ = "Salo Soja Edwin"
__license__ = "MIT"
from .avachain import (
    LLM,
    BaseTool,
    CallbackHandler,
    OpenaiLLM,
    convert_functions_to_json,
    convert_tools_to_json,
    extract_function_info,
    find_and_execute_tool,
)
from .avachain_executor import AvaAgent
from .avachain_utils import resource_path
from .persona_creator import (
    TypeMapping,
    prepare_tools_config,
    push_to_store,
    upload_file,
    validate_logo_path,
)
from .tool_creator import (
    convert_tool_to_json,
    makePluginServerRequest,
    map_type_to_json,
)

# Define the public API for the package
__all__ = [
    # Core classes from avachain module
    "BaseTool",
    "LLM",
    "OpenaiLLM",
    "CallbackHandler",
    # Main agent class from avachain_executor
    "AvaAgent",
    # Utility functions from avachain_utils
    "resource_path",
    # Tool creation functions from tool_creator
    "convert_tool_to_json",
    "makePluginServerRequest",
    "map_type_to_json",
    # Persona management from persona_creator
    "push_to_store",
    "upload_file",
    "validate_logo_path",
    "prepare_tools_config",
    "TypeMapping",
    # Core utility functions (exported from avachain module)
    "convert_tools_to_json",
    "convert_functions_to_json",
    "extract_function_info",
    "find_and_execute_tool",
]

__version__ = "2.0.6"
__author__ = "Salo Soja Edwin"
__license__ = "MIT"

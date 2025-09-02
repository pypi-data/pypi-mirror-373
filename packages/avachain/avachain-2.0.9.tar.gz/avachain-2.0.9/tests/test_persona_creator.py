"""
Unit tests for persona_creator module.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from avachain.persona_creator import (
    convert_tool_to_json,
    prepare_tools_config,
    push_to_store,
    upload_file,
    validate_logo_path,
)


class TestValidateLogoPath:
    """Test cases for validate_logo_path function."""

    def test_validate_nonexistent_file(self):
        """Test validation fails for nonexistent file."""
        with pytest.raises(ValueError, match="Logo file does not exist"):
            validate_logo_path("/nonexistent/path/logo.png")


class TestPrepareToolsConfig:
    """Test cases for prepare_tools_config function."""

    def test_prepare_tools_config_success(self):
        """Test successful tools config preparation."""
        # Create mock agent
        mock_agent = Mock()
        mock_agent.sys_prompt_original = "You are a helpful assistant"
        mock_agent.tools_list = []

        result = prepare_tools_config(mock_agent)

        assert result["base_sys_prompt"] == "You are a helpful assistant"
        assert result["tools"] == []

"""Basic tests for redshift-utils-mcp."""

import pytest
from redshift_utils_mcp import __version__


def test_version():
    """Test that version is defined and follows semver format."""
    assert __version__ is not None
    # Check it follows semver format (x.y.z)
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_imports():
    """Test that main modules can be imported."""
    from redshift_utils_mcp import server
    from redshift_utils_mcp.utils import data_api
    
    assert server.mcp is not None
    assert hasattr(data_api, "get_data_api_config")


def test_server_exists():
    """Test that server can be imported."""
    from redshift_utils_mcp.server import mcp
    
    assert mcp is not None
    assert mcp.name == "Redshift Utils MCP Server"
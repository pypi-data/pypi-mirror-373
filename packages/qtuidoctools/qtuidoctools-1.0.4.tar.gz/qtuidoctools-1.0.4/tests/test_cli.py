# this_file: tests/test_cli.py
"""Tests for the qtuidoctools CLI functionality."""

import subprocess
import sys
from io import StringIO
from unittest.mock import patch

from qtuidoctools.__main__ import QtUIDocTools, cli


def test_cli_help():
    """Test that the CLI shows help without errors."""
    result = subprocess.run(
        [sys.executable, "-m", "qtuidoctools", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Fire outputs help to stderr
    output = result.stdout + result.stderr
    assert "qtuidoctools" in output


def test_cli_version():
    """Test that the CLI shows version without errors."""
    result = subprocess.run(
        [sys.executable, "-m", "qtuidoctools", "version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "qtuidoctools, version" in result.stdout


def test_update_help():
    """Test that update command shows help."""
    result = subprocess.run(
        [sys.executable, "-m", "qtuidoctools", "update", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Fire outputs help to stderr
    output = result.stdout + result.stderr
    assert "UI file or folder to YAML files" in output


def test_build_help():
    """Test that build command shows help."""
    result = subprocess.run(
        [sys.executable, "-m", "qtuidoctools", "build", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Fire outputs help to stderr
    output = result.stdout + result.stderr
    assert "YAML files to JSON" in output


def test_cleanup_help():
    """Test that cleanup command shows help."""
    result = subprocess.run(
        [sys.executable, "-m", "qtuidoctools", "cleanup", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Fire outputs help to stderr
    output = result.stdout + result.stderr
    assert "purely technical" in output


def test_qtuidoctools_class_directly():
    """Test that QtUIDocTools class can be instantiated and used directly."""
    tools = QtUIDocTools()
    
    # Test version method directly
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        tools.version()
        output = mock_stdout.getvalue()
        assert "qtuidoctools, version" in output

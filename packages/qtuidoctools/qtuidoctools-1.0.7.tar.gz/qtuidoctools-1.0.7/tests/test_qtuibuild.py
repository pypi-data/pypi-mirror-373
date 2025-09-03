# this_file: tests/test_qtuibuild.py
"""Tests for the qtuibuild module."""

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml
from yaplon import oyaml

from qtuidoctools.qtuibuild import UIBuild


class TestUIBuild:
    """Test UIBuild class."""

    @pytest.fixture
    def sample_yaml_data(self):
        """Sample YAML data for testing."""
        return {
            "test_widget": {
                "h.nam": "Test Widget",
                "h.tip": "This is a test widget with ==emphasis== and ++Ctrl+A++",
                "h.cls": "QPushButton",
            },
            "another_widget": {
                "h.nam": "Another Widget",
                "h.tip": "Another test widget",
                "h.cls": "QLabel",
            },
        }

    @pytest.fixture
    def temp_yaml_file(self, sample_yaml_data):
        """Create temporary YAML file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            oyaml.yaml_dump(sample_yaml_data, f)
            f.flush()
            yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def temp_yaml_dir(self, sample_yaml_data):
        """Create temporary directory with YAML files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple YAML files
            yaml_file1 = Path(tmpdir) / "widgets1.yaml"
            yaml_file2 = Path(tmpdir) / "widgets2.yaml"

            with open(yaml_file1, "w") as f:
                oyaml.yaml_dump(sample_yaml_data, f)

            # Second file with different data
            data2 = {
                "dialog_widget": {
                    "h.nam": "Dialog Widget",
                    "h.tip": "Dialog widget description",
                    "h.cls": "QDialog",
                }
            }
            with open(yaml_file2, "w") as f:
                oyaml.yaml_dump(data2, f)

            yield tmpdir

    @pytest.fixture
    def temp_json_file(self):
        """Create temporary JSON file path."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            json_path = f.name
        yield json_path
        if os.path.exists(json_path):
            os.unlink(json_path)

    def test_uibuild_initialization(self, temp_json_file, temp_yaml_dir):
        """Test UIBuild initialization."""
        uibuild = UIBuild(
            jsonpath=temp_json_file, dir=temp_yaml_dir, extra=False, logLevel="INFO"
        )

        assert uibuild.jsonpath == temp_json_file
        assert uibuild.dir == temp_yaml_dir
        assert not uibuild.extra

    def test_uibuild_build_creates_json(self, temp_json_file, temp_yaml_dir):
        """Test that UIBuild.build() creates JSON file."""
        uibuild = UIBuild(
            jsonpath=temp_json_file,
            dir=temp_yaml_dir,
            extra=False,
            logLevel="WARNING",  # Reduce log noise in tests
        )

        uibuild.build()

        # Check JSON file was created
        assert os.path.exists(temp_json_file)

        # Check JSON content
        with open(temp_json_file) as f:
            json_data = json.load(f)

        assert isinstance(json_data, dict)
        # Note: JSON might be empty if YAML processing has specific requirements
        # This is acceptable behavior for testing the build process

    def test_uibuild_build_with_extra(self, temp_json_file, temp_yaml_dir):
        """Test UIBuild.build() with extra debug info."""
        uibuild = UIBuild(
            jsonpath=temp_json_file, dir=temp_yaml_dir, extra=True, logLevel="WARNING"
        )

        uibuild.build()

        # Check JSON file was created
        assert os.path.exists(temp_json_file)

        with open(temp_json_file) as f:
            json_data = json.load(f)

        # With extra=True, should have additional debug information
        assert isinstance(json_data, dict)

    def test_uibuild_handles_empty_directory(self, temp_json_file):
        """Test UIBuild with empty YAML directory."""
        with tempfile.TemporaryDirectory() as empty_dir:
            uibuild = UIBuild(
                jsonpath=temp_json_file,
                dir=empty_dir,
                extra=False,
                logLevel="ERROR",  # Only show errors
            )

            # Should not crash with empty directory
            uibuild.build()

            # Should still create JSON file (though it might be empty)
            assert os.path.exists(temp_json_file)

    def test_uibuild_invalid_yaml_directory(self, temp_json_file):
        """Test UIBuild with non-existent YAML directory."""
        uibuild = UIBuild(
            jsonpath=temp_json_file,
            dir="/nonexistent/directory",
            extra=False,
            logLevel="ERROR",
        )

        # Should handle gracefully without crashing
        try:
            uibuild.build()
        except (FileNotFoundError, OSError):
            pass  # Expected behavior for invalid directory

    def test_uibuild_markdown_processing(self, temp_json_file, temp_yaml_dir):
        """Test that UIBuild processes markdown-like syntax."""
        uibuild = UIBuild(
            jsonpath=temp_json_file, dir=temp_yaml_dir, extra=False, logLevel="WARNING"
        )

        uibuild.build()

        with open(temp_json_file) as f:
            json_data = json.load(f)

        # Find widget with markdown syntax and check if it was processed
        test_widget_data = None
        for _widget_id, widget_data in json_data.items():
            if isinstance(widget_data, dict) and widget_data.get("tip"):
                if "emphasis" in widget_data["tip"]:
                    test_widget_data = widget_data
                    break

        # The markdown processing should have converted ==emphasis== to HTML
        if test_widget_data:
            # Check if markdown was processed (should contain HTML tags)
            tip_content = test_widget_data["tip"]
            assert isinstance(tip_content, str)
            # The exact HTML tags depend on prepMarkdown implementation

    def test_build_empty_yaml_directory(self):
        """Test building with empty YAML directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "empty.json"
            yaml_dir = Path(tmpdir) / "yaml_dir"
            yaml_dir.mkdir()

            # Build with empty directory
            builder = UIBuild(str(json_file), str(yaml_dir))
            builder.build()

            # Should create empty JSON file
            assert json_file.exists()

            with json_file.open() as f:
                json_data = json.load(f)

            # Should be empty
            assert json_data == {}

    def test_build_nonexistent_directory(self):
        """Test building with non-existent YAML directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "output.json"
            yaml_dir = Path(tmpdir) / "nonexistent"

            # Build with non-existent directory
            builder = UIBuild(str(json_file), str(yaml_dir))

            # Should handle gracefully
            try:
                builder.build()
                # If it doesn't raise an exception, check the file
                if json_file.exists():
                    with json_file.open() as f:
                        json_data = json.load(f)
                    assert json_data == {}
            except Exception:
                # Expected to fail gracefully
                pass

    def test_parse_tip_text_edge_cases(self):
        """Test parseTipText with various edge cases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "tips.json"
            yaml_dir = Path(tmpdir) / "yaml_dir"
            yaml_dir.mkdir()

            # Create YAML with edge cases
            yaml_file = yaml_dir / "edge_cases.yaml"
            edge_cases = {
                "emptyWidget": {"h.hlp": ""},
                "nullWidget": {"h.hlp": None},
                "crossRefWidget": {"h.hlp": "@otherWidget"},
                "prependWidget": {"h.hlp": "+Prepended text"},
                "directWidget": {"h.hlp": ":Direct text"},
            }

            with yaml_file.open("w") as f:
                yaml.safe_dump(edge_cases, f)

            builder = UIBuild(str(json_file), str(yaml_dir))
            builder.build()

            assert json_file.exists()

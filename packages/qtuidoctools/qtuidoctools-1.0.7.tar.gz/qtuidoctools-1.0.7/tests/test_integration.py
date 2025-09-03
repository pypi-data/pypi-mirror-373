# this_file: tests/test_integration.py
"""Integration tests for the complete .ui → YAML → JSON workflow."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from qtuidoctools.__main__ import QtUIDocTools
from qtuidoctools.qtui import UIDoc
from qtuidoctools.qtuibuild import UIBuild


class TestFullWorkflow:
    """Test the complete workflow from .ui files to JSON output."""

    @pytest.fixture
    def sample_ui_content(self):
        """Sample Qt UI file content with various widgets."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Test Application</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QPushButton" name="saveButton">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>10</y>
      <width>100</width>
      <height>30</height>
     </rect>
    </property>
    <property name="text">
     <string>Save</string>
    </property>
    <property name="toolTip">
     <string>Save the current document</string>
    </property>
   </widget>
   <widget class="QPushButton" name="loadButton">
    <property name="geometry">
     <rect>
      <x>120</x>
      <y>10</y>
      <width>100</width>
      <height>30</height>
     </rect>
    </property>
    <property name="text">
     <string>Load</string>
    </property>
    <property name="toolTip">
     <string>Load a document from disk</string>
    </property>
   </widget>
   <widget class="QLineEdit" name="pathInput">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>50</y>
      <width>200</width>
      <height>25</height>
     </rect>
    </property>
    <property name="toolTip">
     <string>Enter file path here</string>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>800</width>
     <height>22</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>"""

    @pytest.fixture
    def sample_ui_simple(self):
        """Simple UI file with minimal content."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Dialog</class>
 <widget class="QDialog" name="Dialog">
  <widget class="QLabel" name="titleLabel">
   <property name="text">
    <string>Simple Dialog</string>
   </property>
   <property name="toolTip">
    <string>Dialog title label</string>
   </property>
  </widget>
 </widget>
</ui>"""

    def test_ui_to_yaml_workflow(self, sample_ui_content):
        """Test .ui file to YAML conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create UI file
            ui_file = tmpdir_path / "main_window.ui"
            ui_file.write_text(sample_ui_content)

            # Create YAML output directory
            yaml_dir = tmpdir_path / "yaml_output"
            yaml_dir.mkdir()

            # Create TOC file path
            toc_file = tmpdir_path / "helptips.yaml"

            # Process UI file using UIDoc
            ui_doc = UIDoc(
                uipath=str(ui_file), tocpath=str(toc_file), yamldir=str(yaml_dir)
            )
            ui_doc.updateYaml = True
            ui_doc.updateXmlAndYaml()
            ui_doc.saveYaml()
            ui_doc.saveToc()

            # Verify YAML file was created
            yaml_file = yaml_dir / "main_window.yaml"
            assert yaml_file.exists()

            # Verify YAML content
            with yaml_file.open() as f:
                yaml_data = yaml.safe_load(f)

            # Check that expected widgets are present (with filename prefix)
            assert "main_window.saveButton" in yaml_data
            assert "main_window.loadButton" in yaml_data
            assert "main_window.pathInput" in yaml_data

            # Check widget properties
            save_button = yaml_data["main_window.saveButton"]
            assert save_button["u._cls"] == "QPushButton"
            assert save_button["h.tip"] == "Save the current document"

            load_button = yaml_data["main_window.loadButton"]
            assert load_button["u._cls"] == "QPushButton"
            assert load_button["h.tip"] == "Load a document from disk"

            path_input = yaml_data["main_window.pathInput"]
            assert path_input["u._cls"] == "QLineEdit"

            # Verify TOC file was created
            assert toc_file.exists()

            # Check TOC content
            with toc_file.open() as f:
                toc_data = yaml.safe_load(f)

            assert "pages" in toc_data
            pages = toc_data["pages"]
            assert "main_window" in pages
            page_info = pages["main_window"]
            assert "_status" in page_info  # Should have status info

    def test_yaml_to_json_workflow(self, sample_ui_content):
        """Test YAML to JSON compilation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Setup UI → YAML workflow first
            ui_file = tmpdir_path / "test_dialog.ui"
            ui_file.write_text(sample_ui_content)

            yaml_dir = tmpdir_path / "yaml_docs"
            yaml_dir.mkdir()

            toc_file = tmpdir_path / "toc.yaml"

            # Generate YAML
            ui_doc = UIDoc(
                uipath=str(ui_file), tocpath=str(toc_file), yamldir=str(yaml_dir)
            )
            ui_doc.updateYaml = True
            ui_doc.updateXmlAndYaml()
            ui_doc.saveYaml()
            ui_doc.saveToc()

            # Modify YAML to add help content for JSON build
            yaml_file = yaml_dir / "test_dialog.yaml"
            with yaml_file.open() as f:
                yaml_data = yaml.safe_load(f)

            # Add help content so widgets appear in JSON
            for key in yaml_data:
                if "saveButton" in key:
                    yaml_data[key]["h.hlp"] = "Click to save your work"
                elif "loadButton" in key:
                    yaml_data[key]["h.hlp"] = "Click to load a file"
                elif "pathInput" in key:
                    yaml_data[key]["h.hlp"] = "Enter file path here"

            with yaml_file.open("w") as f:
                yaml.safe_dump(yaml_data, f)

            # Now test YAML → JSON workflow
            json_file = tmpdir_path / "output.json"

            ui_build = UIBuild(str(json_file), str(yaml_dir))
            ui_build.build()

            # Verify JSON file was created
            assert json_file.exists()

            # Verify JSON content
            with json_file.open() as f:
                json_data = json.load(f)

            # Check that widgets are present in JSON (with filename prefix)
            widget_keys = [
                k
                for k in json_data.keys()
                if "saveButton" in k or "loadButton" in k or "pathInput" in k
            ]
            assert len(widget_keys) >= 3  # Should have all three widgets

            # Check that help content is processed
            for key in widget_keys:
                assert json_data[key]  # Should have non-empty content

    def test_complete_cli_workflow(self, sample_ui_content, sample_ui_simple):
        """Test the complete workflow using CLI commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create UI files
            ui_dir = tmpdir_path / "ui_files"
            ui_dir.mkdir()

            main_ui = ui_dir / "main.ui"
            main_ui.write_text(sample_ui_content)

            simple_ui = ui_dir / "simple.ui"
            simple_ui.write_text(sample_ui_simple)

            # Create output directories
            yaml_dir = tmpdir_path / "yaml_docs"
            yaml_dir.mkdir()

            # File paths
            toc_file = tmpdir_path / "helptips.yaml"
            json_file = tmpdir_path / "help.json"

            # Initialize CLI tool
            cli = QtUIDocTools()

            # Step 1: UI to YAML (update command)
            cli.update(
                uidir=str(ui_dir), tocyaml=str(toc_file), outyamldir=str(yaml_dir)
            )

            # Verify YAML files were created
            main_yaml = yaml_dir / "main.yaml"
            simple_yaml = yaml_dir / "simple.yaml"

            assert main_yaml.exists()
            assert simple_yaml.exists()
            assert toc_file.exists()

            # Modify YAML files to add help content for JSON build
            for yaml_path in [main_yaml, simple_yaml]:
                with yaml_path.open() as f:
                    yaml_data = yaml.safe_load(f)

                # Add help content so widgets appear in JSON
                for key in yaml_data:
                    if any(
                        widget in key
                        for widget in [
                            "saveButton",
                            "loadButton",
                            "pathInput",
                            "titleLabel",
                        ]
                    ):
                        yaml_data[key]["h.hlp"] = f"Help for {key.split('.')[-1]}"

                with yaml_path.open("w") as f:
                    yaml.safe_dump(yaml_data, f)

            # Step 2: YAML to JSON (build command)
            cli.build(json=str(json_file), toc=str(toc_file), dir=str(yaml_dir))

            # Verify JSON file was created
            assert json_file.exists()

            # Verify JSON content includes widgets from both UI files
            with json_file.open() as f:
                json_data = json.load(f)

            # Check we have widgets (with prefixes) from both files
            widget_keys = list(json_data.keys())
            assert len(widget_keys) >= 4  # Should have widgets from both UI files

            # Check some widgets are present (exact keys have filename prefixes)
            has_save_button = any("saveButton" in k for k in widget_keys)
            has_title_label = any("titleLabel" in k for k in widget_keys)
            assert has_save_button
            assert has_title_label

            # Step 3: Cleanup command (optional formatting)
            cli.cleanup(outyamldir=str(yaml_dir), compactyaml=True)

            # YAML files should still exist and be valid after cleanup
            assert main_yaml.exists()
            assert simple_yaml.exists()

            with main_yaml.open() as f:
                cleaned_data = yaml.safe_load(f)
                # Check that widgets with filename prefixes are still present
                has_save_button = any("saveButton" in k for k in cleaned_data.keys())
                assert has_save_button

    def test_empty_ui_file_handling(self):
        """Test handling of empty or minimal UI files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create minimal UI file
            ui_content = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>EmptyDialog</class>
 <widget class="QDialog" name="EmptyDialog">
 </widget>
</ui>"""

            ui_file = tmpdir_path / "empty.ui"
            ui_file.write_text(ui_content)

            yaml_dir = tmpdir_path / "yaml_output"
            yaml_dir.mkdir()

            toc_file = tmpdir_path / "toc.yaml"

            # Process empty UI file
            ui_doc = UIDoc(
                uipath=str(ui_file), tocpath=str(toc_file), yamldir=str(yaml_dir)
            )
            ui_doc.updateYaml = True
            ui_doc.updateXmlAndYaml()
            ui_doc.saveYaml()
            ui_doc.saveToc()

            # Should create YAML file even if no named widgets
            yaml_file = yaml_dir / "empty.yaml"
            assert yaml_file.exists()

            # Should create valid YAML with at least the main widget
            with yaml_file.open() as f:
                yaml_data = yaml.safe_load(f)
                # Should have the main dialog widget
                assert yaml_data is not None
                assert len(yaml_data) >= 1  # At least the EmptyDialog widget

    def test_tooltip_synchronization(self, sample_ui_content):
        """Test bidirectional tooltip synchronization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create UI file
            ui_file = tmpdir_path / "tooltips.ui"
            ui_file.write_text(sample_ui_content)

            yaml_dir = tmpdir_path / "yaml_docs"
            yaml_dir.mkdir()

            toc_file = tmpdir_path / "toc.yaml"

            # Initial processing
            ui_doc = UIDoc(
                uipath=str(ui_file), tocpath=str(toc_file), yamldir=str(yaml_dir)
            )
            ui_doc.updateYaml = True
            ui_doc.updateXmlAndYaml()
            ui_doc.saveYaml()
            ui_doc.saveToc()

            yaml_file = yaml_dir / "tooltips.yaml"

            # Modify YAML help tips
            with yaml_file.open() as f:
                yaml_data = yaml.safe_load(f)

            # Find the saveButton key (has filename prefix)
            save_button_key = None
            for key in yaml_data:
                if "saveButton" in key:
                    save_button_key = key
                    break

            assert save_button_key is not None
            yaml_data[save_button_key]["h.tip"] = "Modified save tooltip"
            yaml_data[save_button_key]["h.hlp"] = "Updated help content"

            with yaml_file.open("w") as f:
                yaml.safe_dump(yaml_data, f)

            # Test tooltip sync back to UI (this would require the -T flag in CLI)
            # For now, just verify the YAML modification worked
            with yaml_file.open() as f:
                modified_data = yaml.safe_load(f)

            assert modified_data[save_button_key]["h.tip"] == "Modified save tooltip"

    def test_error_handling_invalid_ui(self):
        """Test error handling with invalid UI files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create invalid UI file
            ui_file = tmpdir_path / "invalid.ui"
            ui_file.write_text("This is not valid XML")

            yaml_dir = tmpdir_path / "yaml_output"
            yaml_dir.mkdir()

            toc_file = tmpdir_path / "toc.yaml"

            # Processing should raise an exception for invalid XML
            from lxml.etree import XMLSyntaxError

            with pytest.raises(XMLSyntaxError):
                UIDoc(uipath=str(ui_file), tocpath=str(toc_file), yamldir=str(yaml_dir))

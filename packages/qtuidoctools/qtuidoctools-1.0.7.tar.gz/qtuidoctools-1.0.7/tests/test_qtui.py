# this_file: tests/test_qtui.py
"""Tests for the qtui module."""

import os
import tempfile
from pathlib import Path

import pytest

from qtuidoctools.qtui import UIDoc, getUiPaths, lchop, rchop


class TestUtilityFunctions:
    """Test utility functions."""

    def test_rchop_removes_suffix(self):
        """Test rchop removes substring from end."""
        assert rchop("hello.txt", ".txt") == "hello"
        assert rchop("hello", ".txt") == "hello"  # No change if suffix not found

    def test_lchop_removes_prefix(self):
        """Test lchop removes substring from beginning."""
        assert lchop("prefixhello", "prefix") == "hello"
        assert lchop("hello", "prefix") == "hello"  # No change if prefix not found


class TestGetUiPaths:
    """Test getUiPaths function."""

    def test_getUiPaths_empty_directory(self):
        """Test getUiPaths with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = getUiPaths(dir=tmpdir)
            assert paths == []

    def test_getUiPaths_with_ui_files(self):
        """Test getUiPaths finds .ui files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test .ui files
            ui_file1 = Path(tmpdir) / "test1.ui"
            ui_file2 = Path(tmpdir) / "subdir" / "test2.ui"
            ui_file2.parent.mkdir(exist_ok=True)

            ui_file1.write_text('<?xml version="1.0" encoding="UTF-8"?><ui/>')
            ui_file2.write_text('<?xml version="1.0" encoding="UTF-8"?><ui/>')

            paths = getUiPaths(dir=tmpdir)
            assert len(paths) == 2
            assert any("test1.ui" in p for p in paths)
            assert any("test2.ui" in p for p in paths)

    def test_getUiPaths_single_file(self):
        """Test getUiPaths with single file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ui_file = Path(tmpdir) / "single.ui"
            ui_file.write_text('<?xml version="1.0" encoding="UTF-8"?><ui/>')

            paths = getUiPaths(path=str(ui_file))
            assert len(paths) == 1
            assert str(ui_file) in paths


class TestUIDoc:
    """Test UIDoc class."""

    @pytest.fixture
    def sample_ui_content(self):
        """Sample UI XML content for testing."""
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
   <widget class="QPushButton" name="pushButton">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>10</y>
      <width>80</width>
      <height>24</height>
     </rect>
    </property>
    <property name="text">
     <string>Click Me</string>
    </property>
    <property name="toolTip">
     <string>This is a test button</string>
    </property>
   </widget>
  </widget>
  <action name="actionNew">
   <property name="text">
    <string>&amp;New</string>
   </property>
   <property name="toolTip">
    <string>Create new document</string>
   </property>
  </action>
 </widget>
</ui>"""

    @pytest.fixture
    def temp_ui_file(self, sample_ui_content):
        """Create temporary UI file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ui", delete=False) as f:
            f.write(sample_ui_content)
            f.flush()
            yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def temp_yaml_dir(self):
        """Create temporary YAML directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_uidoc_initialization(self, temp_ui_file, temp_yaml_dir):
        """Test UIDoc initialization."""
        uidoc = UIDoc(uipath=temp_ui_file, yamldir=temp_yaml_dir)
        assert uidoc.uipath == temp_ui_file
        assert uidoc.root is not None
        assert uidoc.docname == Path(temp_ui_file).stem

    def test_uidoc_initialization_with_invalid_file(self, temp_yaml_dir):
        """Test UIDoc initialization with non-existent file."""
        with pytest.raises((FileNotFoundError, OSError)):
            UIDoc(uipath="/nonexistent/file.ui", yamldir=temp_yaml_dir)

    def test_uidoc_basic_properties(self, temp_ui_file, temp_yaml_dir):
        """Test basic UIDoc properties."""
        uidoc = UIDoc(uipath=temp_ui_file, yamldir=temp_yaml_dir)

        # Check that XML was loaded
        assert uidoc.root is not None
        assert uidoc.root.tag == "ui"

        # Check document name extraction
        assert uidoc.docname == Path(temp_ui_file).stem

    def test_uidoc_widget_processing(self, temp_ui_file, temp_yaml_dir):
        """Test that UIDoc can process widgets."""
        uidoc = UIDoc(uipath=temp_ui_file, yamldir=temp_yaml_dir)

        # Find widgets in the loaded XML
        widgets = list(uidoc.root.iter("widget"))
        actions = list(uidoc.root.iter("action"))

        assert len(widgets) >= 2  # MainWindow and pushButton at minimum
        assert len(actions) >= 1  # actionNew

        # Check specific widget exists
        pushButton = None
        for widget in widgets:
            if widget.get("name") == "pushButton":
                pushButton = widget
                break

        assert pushButton is not None
        assert pushButton.get("class") == "QPushButton"

    def test_init_without_yamldir(self):
        """Test UIDoc initialization without yamldir raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ui_file = Path(tmpdir) / "test.ui"
            ui_file.write_text('<?xml version="1.0"?><ui></ui>')
            toc_file = Path(tmpdir) / "toc.yaml"

            with pytest.raises(ValueError, match="Output directory"):
                UIDoc(uipath=str(ui_file), tocpath=str(toc_file), yamldir=None)

    def test_init_missing_ui_file(self):
        """Test UIDoc initialization with missing UI file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_dir = Path(tmpdir) / "yaml"
            yaml_dir.mkdir()
            toc_file = Path(tmpdir) / "toc.yaml"

            with pytest.raises(FileNotFoundError):
                UIDoc(
                    uipath="/nonexistent/file.ui",
                    tocpath=str(toc_file),
                    yamldir=str(yaml_dir),
                )

    def test_process_various_widget_types(self, sample_ui_content):
        """Test processing UI with various widget types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            ui_file = tmpdir_path / "widgets.ui"
            ui_file.write_text(sample_ui_content)

            yaml_dir = tmpdir_path / "yaml"
            yaml_dir.mkdir()

            toc_file = tmpdir_path / "toc.yaml"

            ui_doc = UIDoc(
                uipath=str(ui_file),
                tocpath=str(toc_file),
                yamldir=str(yaml_dir),
                emptytoyaml=True,  # Include empty widgets
            )

            ui_doc.updateYaml = True
            ui_doc.updateXmlAndYaml()
            ui_doc.saveYaml()

            # Check that YAML was created even with various widget types
            yaml_file = yaml_dir / "widgets.yaml"
            assert yaml_file.exists()

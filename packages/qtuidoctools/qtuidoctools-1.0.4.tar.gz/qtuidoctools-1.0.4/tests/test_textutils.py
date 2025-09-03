# this_file: tests/test_textutils.py
"""Tests for the textutils module."""

from qtuidoctools.textutils import keymap, prepMarkdown


def test_prepMarkdown_empty():
    """Test prepMarkdown with empty string."""
    assert prepMarkdown("") == ""


def test_prepMarkdown_basic_text():
    """Test prepMarkdown with basic text."""
    result = prepMarkdown("Hello world")
    assert result == "Hello world"


def test_prepMarkdown_bold():
    """Test prepMarkdown with bold text."""
    result = prepMarkdown("**bold text**")
    assert result == "<b>bold text</b>"


def test_prepMarkdown_italic():
    """Test prepMarkdown with italic text."""
    result = prepMarkdown("*italic text*")
    assert result == "<i>italic text</i>"


def test_prepMarkdown_code():
    """Test prepMarkdown with code spans."""
    result = prepMarkdown("`code span`")
    assert result == "<code>code span</code>"


def test_prepMarkdown_line_breaks():
    """Test prepMarkdown with line breaks."""
    result = prepMarkdown("line1\nline2")
    assert result == "line1<br/>line2"


def test_keymap_exists():
    """Test that keymap dictionary exists and has expected keys."""
    assert isinstance(keymap, dict)
    assert "click" in keymap
    assert "a" in keymap
    assert keymap["a"] == "A"

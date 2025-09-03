#!/usr/bin/env python3
# this_file: src/qtuidoctools/textutils.py
"""Text processing utilities for Qt UI documentation.

This module provides comprehensive markdown-like text processing capabilities
for Qt help tips, including keyboard shortcut formatting, emphasis markup,
and small caps formatting.

Based on an idea by Adam Twardoch and coded by Isaac Muse.
Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>
Modernized for Python 3.11+ compatibility.
"""

import re

try:
    from .keymap_db import aliases, keymap
except ImportError:
    # Fallback for standalone execution
    import sys

    sys.path.append(".")
    from keymap_db import aliases, keymap

__all__ = ["prepMarkdown", "KeysPattern", "MarkPattern", "SmallPattern", "keymap_extra"]


keymap_extra = {
    "space": "<small>SPACE</small>",
    "arrow-up": "↑",
    "arrow-down": "↓",
    "arrow-left": "←",
    "arrow-right": "→",
    "page-up": "<small>PG</small>U<small>P</small>",
    "page-down": "<small>PG</small>D<small>N</small>",
    "backspace": "<small>BKSP</small>",
    "delete": "<small>DEL</small>",
    "insert": "<small>INS</small>",
    "escape": "<small>ESC</small>",
    "alt": "<small>ALT</small>",
    "command": "<small>CMD</small>",
    "control": "<small>CTRL</small>",
    "function": "<small>FN</small>",
    "shift": "<small>SHIFT</small>",
    "click": "click",
    "double-click": "2×click",
    "drag": "drag",
    "drag-drop": "drag-drop",
    "tab": "⇥",
    "enter": "↩",
    "menu-button": "☰",
    "close-button": "✕",
    "gear-button": "☼",
    "update-button": "↻",
    "auto-button": "♥",
    "turn-on": "✓",
    "turn-off": "□",
    "mac": "<sup>M</sup>",
    "windows": "<sup>W</sup>",
}

RE_KBD = r"""(?x)
(?:
    # Escape
    (?<!\\)(?P<escapes>(?:\\{2})+)(?=\+)|
    # Key
    (?<!\\)\+{2}
    (
        (?:(?:[\w\-]+|"(?:\\.|[^"])+"|\'(?:\\.|[^\'])+\')\+)*?
        (?:[\w\-]+|"(?:\\.|[^"])+"|\'(?:\\.|[^\'])+\')
    )
    \+{2}
)
"""
STX = "\u0002"  # Use STX ("Start of text") for start-of-placeholder
ETX = "\u0003"  # Use ETX ("End of text") for end-of-placeholder
ESCAPE_RE = re.compile(r"""(?<!\\)(?:\\\\)*\\(.)""")
UNESCAPED_PLUS = re.compile(r"""(?<!\\)(?:\\\\)*(\+)""")
BACKSLASH_ORD = ord("\\")
ESCAPED_BSLASH = STX + str(BACKSLASH_ORD) + ETX
DOUBLE_BSLASH = "\\\\"


class KeysPattern:
    """Return kbd tag."""

    def __init__(self, md: str, pattern: str = RE_KBD) -> None:
        """Initialize."""

        self.ksep = "+"
        self.kbefore = ""
        self.kafter = ""
        self.strict = False
        self.classes = ["keys"]
        self.map = self.merge(keymap, keymap_extra)
        self.aliases = aliases
        self.camel = True
        self.pattern = pattern
        self.compiled_re = re.compile(pattern, re.DOTALL | re.UNICODE)
        self.md = md

    def merge(self, x: dict[str, str], y: dict[str, str]) -> dict[str, str]:
        """Given two dicts, merge them into a new dict."""

        z = x.copy()
        z.update(y)
        return z

    def normalize(self, key: str) -> str:
        """Normalize the value."""

        if not self.camel:
            return key

        norm_key = []
        last = ""
        for c in key:
            if c.isupper():
                if not last or last == "-":
                    norm_key.append(c.lower())
                else:
                    norm_key.extend(["-", c.lower()])
            else:
                norm_key.append(c)
            last = c
        return "".join(norm_key)

    def process_key(self, key: str) -> tuple[str | None, str] | None:
        """Process key."""

        if key.startswith(('"', "'")):
            # Disabling HTML unescaping of quoted keys, it's too dependency-heavy
            value = (
                None,
                key[1:-1],
            )  # (None, util.html_unescape(ESCAPE_RE.sub(r'\1', key[1:-1])).strip())
        else:
            norm_key = self.normalize(key)
            canonical_key = self.aliases.get(norm_key, norm_key)
            name = self.map.get(canonical_key, None)
            value = (canonical_key, name) if name else None
        return value

    def handleMatch(self, m):
        """Handle kbd pattern matches."""
        if m.group(1):
            return m.group("escapes").replace(DOUBLE_BSLASH, ESCAPED_BSLASH)
        content = [
            self.process_key(key)
            for key in UNESCAPED_PLUS.split(m.group(2))
            if key != "+"
        ]

        if None in content:
            return None

        el = (
            self.kbefore
            + self.ksep.join([f"<b>{c[1]}</b>" for c in content])
            + self.kafter
        )
        el = el.replace("<b><sup>", "<sup>")
        el = el.replace("</sup></b>", "</sup>")
        el = el.replace(self.ksep + "<sup>", "<sup>")
        el = el.replace("</sup>" + self.ksep, "</sup>")
        return el

    def sub(self):
        return self.compiled_re.sub(self.handleMatch, self.md)


class MarkPattern:
    CONTENT = r"((?:[^=]|(?<!={2})=)+?)"
    # ==mark==
    MARK = rf"(={{2}})(?!\s){CONTENT}(?<!\s)\1"

    def __init__(self, md):
        """Initialize."""

        self.ksep = "›"
        self.kbefore = ""
        self.kafter = ""
        self.compiled_re = re.compile(self.MARK, re.DOTALL | re.UNICODE)
        self.md = md

    def handleMatch(self, m):
        el = m.group(2).replace(">", self.ksep)
        el = self.kbefore + el + self.kafter
        return el

    def sub(self):
        return self.compiled_re.sub(self.handleMatch, self.md).replace("\\=", "=")


class SmallPattern:
    CONTENT = r"((?:[^\^]|(?<!\^{2})\^)+?)"
    # ==mark==
    SMALL = rf"(\^{{2}})(?!\s){CONTENT}(?<!\s)\1"

    def __init__(self, md):
        """Initialize."""

        self.kbefore = "<small>"
        self.kafter = "</small>"
        self.compiled_re = re.compile(self.SMALL, re.DOTALL | re.UNICODE)
        self.md = md

    def handleMatch(self, m):
        el = m.group(2)
        el = self.kbefore + el + self.kafter
        return el

    def sub(self):
        return self.compiled_re.sub(self.handleMatch, self.md)


reLf = re.compile(r"(\n\n+)", flags=re.MULTILINE)


def prepMarkdown(md: str) -> str:
    """Prepare markdown-like text for display in Qt help tips.

    This function processes text with advanced markdown-like syntax including:
    - Keyboard shortcuts (++key++ patterns)
    - Emphasis markup (==text== patterns)
    - Small caps (^^text^^ patterns)
    - Special text replacements

    Args:
        md: Input text with markdown-like syntax

    Returns:
        Processed HTML text ready for Qt display
    """
    md = md.replace(">>", "‣")
    md = md.replace("???", "||^^MORE: Help › User Manual^^")
    md = md.replace("??", "||^^MORE: SHIFT·F1 when this is active^^")
    md = md.replace("|||", "<br/>")
    md = md.replace("||", "\n\n")
    md = re.sub(reLf, r"\n\n", md)
    mp = MarkPattern(md)
    mp.kbefore = "<i>"
    mp.kafter = "</i>"
    mp.ksep = "›"
    md = mp.sub()
    md = SmallPattern(md).sub()
    kp = KeysPattern(md)
    kp.ksep = "·"  # chr(0x202F)
    kp.kbefore = '<span style="font-style: normal; white-space: nowrap;">'
    kp.kafter = "</span>"
    md = kp.sub()
    return md


if __name__ == "__main__":
    md = 'Press ++Shift+Alt+PgUp++, type in ++"Hello"++, press ++Win+Left++ and ++Enter++.'
    kp = KeysPattern(md)
    print(kp.sub())
    md = r"Choose ==Preferences > General== or click on ==+== and ==\===."
    kp = MarkPattern(md)
    print(kp.sub())
    md = "Choose ^^Preferences > General^^ or click on ^^Ob^^ and ^^a^^."
    kp = SmallPattern(md)
    print(kp.sub())

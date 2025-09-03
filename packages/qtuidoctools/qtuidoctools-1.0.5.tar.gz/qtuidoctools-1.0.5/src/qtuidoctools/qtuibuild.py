#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["PyYAML>=5.1.1"]
# ///
# this_file: src/qtuidoctools/qtuibuild.py
# -*- coding: utf-8 -*-
"""
QtUIBuild - A tool for compiling JSON help tips from YAML documentation files.

This script processes YAML files containing help tip definitions and converts them
into a single JSON file for use in Qt applications. It supports text processing
with markdown-like syntax and cross-references between tips.
"""

__version__ = "0.0.3"

import datetime
import glob
import json
import os
import plistlib
from collections import OrderedDict
from typing import Any

import yaml

try:
    from .textutils import prepMarkdown
except ImportError:
    # Fallback for standalone execution
    import sys

    sys.path.append(".")
    from textutils import prepMarkdown

# - Exports -------------------------------------------------------------------
__all__ = ["UIBuild", "getYamlPaths", "read_yaml"]

# - Globals -------------------------------------------------------------------
# List of widget IDs to debug during processing - add IDs here for detailed logging
PRINTDEBUG: list[str] = []  # ['info_codepages.checkSymbol']

# - Functions -----------------------------------------------------------------


def read_yaml(stream: Any, loader: Any = yaml.Loader) -> Any:
    """
    Load YAML with custom constructors for consistent data types.

    Makes all YAML dictionaries load as OrderedDicts and handles special data types
    like binary data, timestamps, and regex patterns consistently.

    Args:
        stream: YAML input stream
        loader: YAML loader class to use

    Returns:
        Parsed YAML data structure

    Reference: http://stackoverflow.com/a/21912744/3609487
    """

    def binary_constructor(self, node):
        return plistlib.Data(self.construct_yaml_binary(node))

    def timestamp_constructor(self, node):
        timestamp = self.construct_yaml_timestamp(node)
        if not isinstance(timestamp, datetime.datetime):
            return str(timestamp)
        microsecond_str = (
            f".{timestamp.microsecond:06d}" if timestamp.microsecond != 0 else ""
        )
        return (
            f"{timestamp.year:04d}-{timestamp.month:02d}-{timestamp.day:02d}T"
            f"{timestamp.hour:02d}:{timestamp.minute:02d}:{timestamp.second:02d}"
            f"{microsecond_str}Z"
        )

    def construct_mapping(loader_instance, node):
        loader_instance.flatten_mapping(node)
        return OrderedDict(loader_instance.construct_pairs(node))

    class CustomLoader(loader):
        pass

    CustomLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )
    CustomLoader.add_constructor("tag:yaml.org,2002:binary", binary_constructor)
    CustomLoader.add_constructor("tag:yaml.org,2002:timestamp", timestamp_constructor)
    CustomLoader.add_constructor(
        "tag:yaml.org,2002:regex", CustomLoader.construct_yaml_str
    )

    return yaml.load(stream, CustomLoader)


def getYamlPaths(path: str = "*.yaml", dir: str | None = None) -> list[str]:
    """Get list of YAML file paths matching the given pattern.

    Args:
        path: Glob pattern for YAML files (default: '*.yaml')
        dir: Directory to search in (if None, uses current directory)

    Returns:
        List of matching file paths
    """
    if dir:
        return glob.glob(os.path.join(dir, path))
    elif os.path.exists(path):
        return [path]
    return []


# - Classes -------------------------------------------------------------------


class UIBuild:
    """
    Class that compiles JSON help tips from YAML documentation files.

    This class processes a directory of YAML files containing help tip definitions
    and converts them into a single JSON file suitable for Qt applications.
    It supports text processing, cross-references, and development mode extras.
    """

    def __init__(
        self, jsonpath: str, dir: str, extra: bool = False, logLevel: str = "INFO"
    ) -> None:
        """Initialize the UIBuild processor.

        Args:
            jsonpath: Output path for the generated JSON file
            dir: Directory containing YAML source files
            extra: Enable development mode with extra widget ID information
            logLevel: Logging level ('INFO', 'DEBUG', etc.)
        """
        self.jsonpath: str = jsonpath
        self.dir: str = dir
        self.extra: bool = extra
        self.logLevel: str = logLevel
        self.jsontips: OrderedDict[str, Any] = OrderedDict()
        self.yamltips: OrderedDict[str, Any] = OrderedDict()
        self.toc: dict[str, list[str]] = {
            "pages": getYamlPaths(path="*.yaml", dir=self.dir)
        }

    def parseTipText(
        self, wid: str, prop: str = "h.hlp", fallback: str | None = None
    ) -> str | None:
        """Parse and process tip text for a widget ID.

        This method handles various text processing features:
        - Cross-references (starting with '@')
        - Text prepending (starting with '+')
        - Direct text (starting with ':')
        - Automatic heading formatting

        Args:
            wid: Widget ID to process
            prop: Property name to extract (default: 'h.hlp')
            fallback: Fallback property name if main property is empty

        Returns:
            Processed tip text or None if no text found
        """
        rid = wid
        raw = self.yamltips.get(wid, {}).get(prop)

        if wid in PRINTDEBUG:
            print(f'GETTIP:{wid} ({prop}): "{raw}"')

        if raw:
            raw = str(raw).strip()

        if not raw and fallback:
            raw = self.yamltips.get(wid, {}).get(fallback)
            if wid in PRINTDEBUG:
                print(f'GETTIP:{wid} ({fallback}): "{raw}"')
            if raw:
                raw = str(raw).strip()

        if not raw:
            return None

        text = raw
        if raw.startswith(":"):
            text = raw[1:]
        elif raw.startswith("@"):
            if raw[1:] in self.yamltips:
                rid = raw[1:]
                text = self.parseTipText(rid, prop, fallback)
            else:
                text = self.yamltips.get(wid, {}).get(fallback)
        elif raw.startswith("+"):
            add = "+"
            if prop in ("h.hlp", "h.hlp_"):
                add = self.parseTipText(rid, "h.nam") or "+"
            elif prop == "h.nam":
                add = self.parseTipText(rid, "h.tip") or "+"

            if len(raw) == 1:
                text = add
            elif len(raw) > 1:
                if raw[1] == "#":
                    text = f"# {add}" if len(raw) == 2 else f"# {add}||{raw[2:]}"
                elif raw[1] == "*":
                    text = f"**{add}**" if len(raw) == 2 else f"**{add}**: {raw[2:]}"
                elif raw[1] == ".":
                    text = f"{add}{raw[2:]}"
                else:
                    text = f"{add}: {raw[1:]}"

        if text:
            text = str(text).strip()
            if text.startswith("#") and not text.startswith("##"):
                text = f"#### {text[1:]}"

        if wid in PRINTDEBUG:
            print(f'PARSE:{wid}/{rid} ({prop}): "{raw}" > "{text}"')

        return text

    def build(self) -> None:
        """Build the JSON help tips file from YAML sources.

        This method:
        1. Loads all YAML files from the source directory
        2. Processes each widget ID's help text
        3. Applies text processing and formatting
        4. Outputs warnings for overly long help texts
        5. Saves the final JSON file
        """
        # Load all YAML files into the yamltips dictionary
        for yamlpath in self.toc["pages"]:
            with open(yamlpath, encoding="utf-8") as f:
                self.yamltips.update(read_yaml(f))

        # Process each widget ID in the loaded YAML data
        for wid in self.yamltips:
            raw = self.parseTipText(wid, "h.hlp", "h.hlp_")
            # Warn about overly long help texts (impacts UI performance)
            if raw and (
                (len(raw) > 1252 and "^^" in raw)
                or (len(raw) > 700 and "^^" not in raw)
            ):
                print(f"\nWARNING:{wid} length is {len(raw)}:\n>> {raw}\n")

            if wid in PRINTDEBUG:
                print(f'TRY:{wid}: "{raw}"')

            text = raw
            # Add development mode extras (widget ID display)
            if self.extra and "." in wid:
                pref, _, suf = wid.partition(".")
                if pref not in ("app", "q"):
                    if text:
                        text += f"\n\n<small style='color: #d2d3d4;'>{pref}.<tt>{suf}</tt></small>"
                    else:
                        nam_text = self.parseTipText(wid, "h.nam", "h.tip")
                        text = (
                            f"<div style='background-color: black; color: white;'>{nam_text}</div>"
                            if nam_text
                            else ""
                        )
                        text += f"<small style='background-color: black; color: white;'>&nbsp;{pref}.<tt>{suf}</tt>&nbsp;</small>"

            if text:
                self.jsontips[wid] = prepMarkdown(text)

            if wid in PRINTDEBUG:
                print(f'BUILD:{wid}: "{raw}" > "{text}"')

        # Sort tips alphabetically by widget ID for consistent output
        self.jsontips = OrderedDict(sorted(self.jsontips.items(), key=lambda t: t[0]))

        # Write the final JSON file
        with open(self.jsonpath, "w", encoding="utf-8") as f:
            json.dump(self.jsontips, f, ensure_ascii=False, separators=(",", ":"))

        # Log completion information
        if self.logLevel in ["INFO", "DEBUG"]:
            print(f"INFO: Saved {self.jsonpath}")
            if self.extra:
                print("INFO: with devel IDs")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: qtuibuild.py <main_directory>")
        print("  Builds helptips.json from YAML files in <main_directory>/yaml/")
        sys.exit(1)

    maindir = sys.argv[1]
    jsonpath = os.path.join(maindir, "helptips.json")
    yamldir = os.path.join(maindir, "yaml")

    if not os.path.isdir(yamldir):
        print(f"ERROR: YAML directory not found: {yamldir}")
        sys.exit(1)

    uib = UIBuild(dir=yamldir, jsonpath=jsonpath)
    uib.build()

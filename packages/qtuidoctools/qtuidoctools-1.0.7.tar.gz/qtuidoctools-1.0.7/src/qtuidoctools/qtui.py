#!/usr/bin/env -S uv run -s
# /// script
# dependencies = [
#   "lxml>=4.4.1",
#   "PyYAML>=5.1.1",
#   "Qt.py>=1.2.1",
#   "yaplon",
#   "click>=7.0",
# ]
# ///
# this_file: src/qtuidoctools/qtui.py
# -*- coding: utf-8 -*-
"""
This script processes Qt UI files (.ui) to extract and manage help tips.
It reads metadata from the UI files, updates a YAML table of contents,
and can generate YAML files with help tip information.
"""

__version__: str = "0.0.4"

import datetime
import logging
import os.path
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

from lxml import etree
from yaplon import oyaml

from .qtuibuild import UIBuild, prepMarkdown

# - Exports -------------------------------------------------------------------
__all__ = ["getUiPaths", "UIDoc", "rchop", "lchop"]

# - Globals -------------------------------------------------------------------
PRINTDEBUG: list[str] = []  # Add widget IDs here to enable extra debug logging


# - Functions -----------------------------------------------------------------
def rchop(s: str, sub: str) -> str:
    """Remove a substring from the end of a string."""
    if s.endswith(sub):
        return s[: -len(sub)]
    return s


def lchop(s: str, sub: str) -> str:
    """Remove a substring from the beginning of a string."""
    if s.startswith(sub):
        return s[len(sub) :]
    return s


def getUiPaths(path: str = "*.ui", dir: str | None = None) -> list[str]:
    """Get a list of UI file paths."""
    paths: list[str] = []
    if dir:
        for p in Path(dir).glob("**/" + path):
            paths.append(str(p))
    elif os.path.exists(path):
        paths = [path]
    return paths


# - Classes -------------------------------------------------------------------
class UIDoc:
    """
    Class that deals with a single QtUI XML file.
    It can extract widget information, update help tips in both XML and YAML formats,
    and maintain a table of contents.
    """

    reNumXPath = re.compile(r"(^.*)\[(\d+?)\]$")
    reMenuText = re.compile(r"(&)(?!&)")

    def __init__(
        self,
        uipath: str,
        logLevel: str = "INFO",
        tocpath: str | None = None,
        yamldir: str | None = None,
        emptytoyaml: bool = False,
        alwayssaveyaml: bool = False,
    ):
        """
        Initializes the UIDoc object.

        :param uipath: path to the UI XML file
        :param logLevel: logging level
        :param tocpath: path to the YAML Table of contents file
        :param yamldir: folder to write the YAML tips
        :param emptytoyaml: emit widget info that has no metadata if True
        """

        # Internal options
        self.devWriteCls: bool = True
        self.devAddEmptyHlp: bool = True

        # External options
        self.tocpath: str | None = tocpath
        self.outdir: str | None = yamldir
        self.outempty: bool = emptytoyaml
        self.rebuildStatusTipsInXml: bool = False
        self.replaceToolTipsInXml: bool = False
        self.replaceToolTipsInYaml: bool = False
        self.updateYaml: bool = False
        self.replaceNamInYaml: bool = False
        self.modifiedXml: bool = False
        self.modifiedYaml: bool = alwayssaveyaml
        self.okYaml: bool = True
        self.modifiedToc: bool = False
        self.time: str = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
        self.user: str = os.environ.get("USER", "unknown")

        if not self.outdir:
            raise ValueError("Output directory 'yamldir' is required.")
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        if uipath and os.path.exists(uipath):
            self.uipath: str = uipath
            self.setUp(logLevel=logLevel)
            self.openToc()
            self.openXml()
            self.openYaml()
        else:
            raise FileNotFoundError(f"UI file does not exist: {uipath}")

    def msg(self, msg: tuple) -> str:
        """Formats a log message."""
        return " ".join([str(i) for i in msg]) + "\n"

    def log(self, *msg: Any) -> None:
        """Log as debug."""
        self.logger.debug(self.msg(msg))

    def print(self, *msg: Any) -> None:
        """Log as info."""
        self.logger.info(self.msg(msg))

    def warn(self, *msg: Any) -> None:
        """Log as warning."""
        self.logger.warning(self.msg(msg))

    def err(self, *msg: Any) -> None:
        """Log as error."""
        self.logger.error(self.msg(msg))

    def pprint(self, o: Any) -> None:
        """Pretty-print object as YAML."""
        self.print(self.toYaml(o))

    def toYaml(
        self, o: Any, quote_strings: bool = False, block_strings: bool = True
    ) -> str:
        """Converts an object to a YAML string."""
        return oyaml.yaml_dumps(
            o,
            compact=False,
            width=0,
            quote_strings=quote_strings,
            block_strings=block_strings,
            indent=2,
            double_quote=True,
        )

    def setUp(self, logLevel: str = "INFO") -> None:
        """Prepare the object."""
        self.docname: str = os.path.splitext(os.path.split(self.uipath)[1])[0]
        self.yamlpath: str = os.path.join(self.outdir, self.docname + ".yaml")
        self.doc: OrderedDict[str, Any] = OrderedDict()
        logging.basicConfig(level=logLevel)
        self.logger: logging.Logger = logging.getLogger(self.docname)
        self.xps: OrderedDict[str, Any] = OrderedDict()
        self.xpsrep: OrderedDict[str, Any] = OrderedDict()
        self.tree: etree._ElementTree | None = None
        self.root: etree._Element | None = None
        self.tips: OrderedDict[str, Any] = OrderedDict()
        self.toc: OrderedDict[str, Any] = OrderedDict()

    def openXml(self) -> None:
        """Read self.tree from XML UI file."""
        self.tree = etree.parse(self.uipath)
        self.root = self.tree.getroot()
        self.log("> Opened UI:", os.path.split(self.uipath)[1])

    def saveXml(self, uipath: str | None = None) -> None:
        """Save self.tree into XML UI file."""
        uipath = uipath if uipath else self.uipath
        if self.modifiedXml and self.tree is not None:
            self.tree.write(
                file=uipath, xml_declaration=True, encoding="utf-8", pretty_print=True
            )
            self.print("> Saved UI:", uipath)

    def setModifiedXml(self) -> None:
        """Marks the XML as modified and updates the TOC."""
        self.modifiedXml = True
        self.updateTocMod()

    def setModifiedYaml(self) -> None:
        """Marks the YAML as modified and updates the TOC."""
        self.modifiedYaml = True
        self.updateTocMod()

    def updateTocMod(self) -> None:
        """Updates the modification status in the TOC."""
        self.updateTocProp("_status", f"EDITING by {self.user}")
        self.updateTocProp("_mod", f"{self.user} {self.time}")
        self.modifiedToc = True

    def openToc(self) -> None:
        """Read YAML file into self.toc."""
        if self.tocpath and os.path.exists(self.tocpath):
            with open(self.tocpath) as f:
                self.toc = oyaml.read_yaml(f)
        else:
            self.toc = OrderedDict([("pages", OrderedDict())])

    def saveToc(self) -> None:
        """Save self.toc as YAML file."""
        if self.modifiedToc and self.tocpath:
            with open(self.tocpath, "w") as f:
                f.write(self.toYaml(self.toc, quote_strings=False, block_strings=False))
            self.log("> Saved TOC:", self.tocpath)

    def pruneYaml(self) -> None:
        """Cleans up the YAML data before saving."""
        if not self.tips:
            self.err(f"Cannot prune YAML {self.yamlpath}")
            self.okYaml = False
            return

        for k in self.tips:
            d = self.tips[k]
            if "u.cls" in d:
                del d["u.cls"]
            if "u.tip" in d:
                del d["u.tip"]
            if not self.devWriteCls and "u._cls" in d:
                del d["u._cls"]
            if self.devAddEmptyHlp and "h.hlp" not in d:
                d["h.hlp"] = ""
            for i in d:
                if isinstance(d[i], str):
                    d[i] = d[i].replace("\u000a", "").replace("\u000d", "")
            self.tips[k] = OrderedDict(sorted(d.items(), key=lambda t: t[0]))

    def openYaml(self) -> None:
        """Read YAML file into self.tips."""
        if os.path.exists(self.yamlpath):
            with open(self.yamlpath) as f:
                self.tips = oyaml.read_yaml(f)
            self.log("> Opened YAML:", os.path.split(self.yamlpath)[1])
        else:
            self.tips = OrderedDict()

    def saveYaml(self) -> None:
        """Write self.tips as YAML file."""
        self.pruneYaml()
        if self.modifiedYaml:
            with open(self.yamlpath, "w") as f:
                f.write(self.toYaml(self.tips, quote_strings=True, block_strings=True))
            self.log("> Saved YAML:", self.yamlpath)

    def updateTocProp(self, prop: str | None = None, val: str = "") -> None:
        """Update Table of contents entry."""
        if "pages" not in self.toc:
            self.toc["pages"] = OrderedDict()

        if self.docname not in self.toc["pages"]:
            self.toc["pages"][self.docname] = OrderedDict()
            self.modifiedToc = True

        if prop:
            self.toc["pages"][self.docname][prop] = val
            self.modifiedToc = True

    def getnicepath(self, el: etree._Element) -> str:
        """Gets a user-friendly path for an element."""
        if self.tree is None:
            return ""
        xpkey = self.tree.getpath(el)
        return self.xps.get(xpkey, xpkey)

    def updateToc(self) -> None:
        """Update Table of contents."""
        if self.root is None:
            return
        self.updateTocProp()
        p_className = self.root.xpath("//class")
        className = p_className[0].text if len(p_className) else None
        if className and self.devWriteCls:
            self.updateTocProp("_cls", className)
        p_windowTitle = self.root.xpath("//widget/property[@name='windowTitle']/string")
        windowTitle = p_windowTitle[0].text if len(p_windowTitle) else None
        if windowTitle:
            self.updateTocProp("_windowTitle", windowTitle)

    def editTipText(self, text: str | None) -> str | None:
        """Edits the tip text if necessary."""
        if text and text.startswith("@"):
            return text
        return text

    def copyPropFromXmlToYaml(
        self,
        el: etree._Element,
        wid: str,
        xmlprop: str = "toolTip",
        yamlprop: str = "u._tip",
        replace: bool = False,
        bakyamlprop: str | None = None,
        outempty: bool = False,
        useText: bool = False,
    ) -> None:
        """
        Find XML property for widget and copy to self.tips ("YAML").
        """
        doCopy = True
        if not self.tips:
            self.tips = OrderedDict()

        if wid not in self.tips:
            self.tips[wid] = OrderedDict()

        if not replace and str(self.tips[wid].get(yamlprop, "")).strip():
            doCopy = False

        if doCopy:
            p_prop = el.xpath(f"./property[@name='{xmlprop}']")
            if p_prop:
                el_prop = p_prop[0]
                p_propString = el_prop.xpath("./string")
                if p_propString and p_propString[0].text:
                    text = p_propString[0].text
                    if xmlprop == "text" and useText:
                        text = self.reMenuText.sub("", text)
                    self.tips[wid][yamlprop] = self.editTipText(text)
                    self.setModifiedYaml()

            if not self.tips[wid].get(yamlprop) and bakyamlprop:
                bak = self.tips[wid].get(bakyamlprop)
                if bak:
                    self.tips[wid][yamlprop] = self.editTipText(bak)
                    self.setModifiedYaml()

        if outempty and not self.tips[wid].get(yamlprop):
            self.tips[wid][yamlprop] = ""
            self.setModifiedYaml()

    def updateTipInXml(
        self,
        el: etree._Element,
        tip: str,
        text: str | None = None,
        delete: bool = False,
    ) -> None:
        """Updates a tip property in the XML element."""
        if not text and not delete:
            return

        p_tip = el.xpath(f"./property[@name='{tip}']")
        if not p_tip:
            el_tip = etree.Element("property", attrib={"name": tip})
            el.append(el_tip)
            self.log(f"> Added UI {tip}: ", text)
            self.setModifiedXml()
            p_tip = el.xpath(f"./property[@name='{tip}']")

        el_tip = p_tip[0]
        p_tipString = el_tip.xpath("./string")
        if not p_tipString:
            el_tipString = etree.Element("string")
            el_tip.append(el_tipString)
            self.setModifiedXml()
            p_tipString = el_tip.xpath("./string")

        el_tipString = p_tipString[0]

        if delete:
            self.print(f"> Deleted {tip}")
            el_tipString.text = ""
            self.setModifiedXml()
        else:
            newtext = prepMarkdown(text) if text else ""
            if el_tipString.text != newtext:
                self.print(f"> Updated {tip}: '{el_tipString.text}' --> '{newtext}'")
                el_tipString.text = newtext
                self.setModifiedXml()

    def updateWidget(self, el: etree._Element) -> None:
        """
        Update a given <widget> or <action> element in XML and its info in YAML.
        """
        widgetName = el.get("name")
        if not widgetName:
            self.err(f"Action or widget has no name: {self.getnicepath(el)}")
            return

        className = el.get("class") if el.tag == "widget" else "QAction"
        wid = f"{self.docname}.{widgetName}"

        if self.rebuildStatusTipsInXml:
            self.updateTipInXml(el, tip="statusTip", text=f"@{wid}")

        if self.updateYaml:
            # Copy 'toolTip' from UI to 'u._tip' in YAML (always replace)
            self.copyPropFromXmlToYaml(
                el, wid, xmlprop="toolTip", yamlprop="u._tip", replace=True
            )
            # Copy 'text' from UI to 'u._txt' in YAML (always replace)
            self.copyPropFromXmlToYaml(
                el, wid, xmlprop="text", yamlprop="u._txt", replace=True, useText=True
            )
            # Copy 'toolTip' from UI to 'h.tip' in YAML
            self.copyPropFromXmlToYaml(
                el,
                wid,
                xmlprop="toolTip",
                yamlprop="h.tip",
                replace=self.replaceToolTipsInYaml,
                outempty=self.outempty,
            )
            # Copy 'toolTip' or 'text' to 'h.nam' in YAML
            self.copyPropFromXmlToYaml(
                el,
                wid,
                xmlprop="toolTip",
                yamlprop="h.nam",
                replace=self.replaceNamInYaml,
                bakyamlprop="h.tip",
                outempty=self.outempty,
            )
            if not self.tips[wid].get("h.nam"):
                self.copyPropFromXmlToYaml(
                    el,
                    wid,
                    xmlprop="text",
                    yamlprop="h.nam",
                    replace=False,
                    outempty=True,
                    useText=True,
                )

            if className and self.devWriteCls:
                if self.tips[wid].get("u._cls") != className:
                    self.tips[wid]["u._cls"] = className
                    self.setModifiedYaml()

            toolTip = self.tips[wid].get("h.tip")
            if toolTip:
                toolTip = str(toolTip).strip().replace("++", "").replace("==", "")

            oldTip = self.tips[wid].get("u._tip", "")
            if self.replaceToolTipsInXml and oldTip != toolTip:
                self.updateTipInXml(el, tip="toolTip", text=toolTip)

            # Import accessibleDescription from UI
            self.copyPropFromXmlToYaml(
                el,
                wid,
                xmlprop="accessibleDescription",
                yamlprop="h.hlp",
                replace=False,
            )

    def updateXmlAndYaml(self) -> None:
        """
        Main method for updating the XML and YAML.
        Runs updateWidget on QtUI elements <widget> and <action>.
        """
        if self.root is None:
            return
        for el in self.root.iter("widget", "action"):
            self.updateWidget(el)

    def prepQtApp(self) -> None:
        """Prepares and shows the UI file as a Qt application for testing.

        Notes:
        - Uses Qt.py compatibility layer; supports PyQt/PySide bindings.
        - Ensures the UI path is absolute before changing the working directory,
          so relative `self.uipath` still resolves correctly after chdir.
        """
        try:
            from Qt import QtCompat, QtWidgets
        except ImportError:
            self.err("Qt.py is not installed. Cannot show the Qt App.")
            return

        cwd = os.getcwd()
        pyuifolder = os.path.join(cwd, "temp_qt_ui")
        os.makedirs(pyuifolder, exist_ok=True)
        # Resolve UI path to absolute path before changing cwd to avoid path issues
        uipath_abs = os.path.abspath(self.uipath)
        os.chdir(pyuifolder)

        self.qtmods = []
        if self.root is not None:
            for xwid in self.root.findall("./customwidgets/*"):
                wcust = xwid.find("class").text
                wqt = xwid.find("extends").text
                wmod = rchop(xwid.find("header").text, ".h")
                pymodpath = os.path.join(pyuifolder, wmod + ".py")
                with open(pymodpath, "w+") as pymod:
                    pymod.write(f"from Qt.QtWidgets import {wqt} as {wcust}\n")
                self.qtmods.append(pymodpath)

        self.qtapp = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        # Use absolute path to ensure load works regardless of cwd
        self.qtui = QtCompat.loadUi(uifile=uipath_abs)
        self.qtui.show()

    def showQtApp(self) -> None:
        """Run the Qt app event loop.

        Uses `exec()` when available (Qt6+), otherwise falls back to `exec_()`
        for compatibility with older bindings.
        """
        if hasattr(self, "qtapp"):
            if hasattr(self.qtapp, "exec"):
                self.qtapp.exec()
            else:
                self.qtapp.exec_()

    def quitQtApp(self) -> None:
        """Quit the Qt app and clean up any temporary modules."""
        if hasattr(self, "qtapp"):
            self.qtapp.quit()
        if hasattr(self, "qtmods"):
            for pymodpath in self.qtmods:
                if os.path.exists(pymodpath):
                    os.remove(pymodpath)

    def update(
        self,
        rebuildStatusTipsInXml: bool = True,
        replaceToolTipsInXml: bool = False,
        replaceToolTipsInYaml: bool = False,
        updateYaml: bool = True,
        replaceNamInYaml: bool = False,
        saveXml: bool = True,
    ) -> None:
        """
        Perform update of XML and/or YAML.
        """
        self.updateToc()

        self.rebuildStatusTipsInXml = rebuildStatusTipsInXml
        self.replaceToolTipsInXml = replaceToolTipsInXml
        self.replaceToolTipsInYaml = replaceToolTipsInYaml
        self.updateYaml = updateYaml
        self.replaceNamInYaml = replaceNamInYaml
        self.updateXmlAndYaml()

        if saveXml:
            self.saveXml()
        if self.okYaml:
            self.saveYaml()
            self.saveToc()
        else:
            self.err(f"YAML not saved: {self.yamlpath}")


if __name__ == "__main__":
    maindir = "../../"
    uipath = maindir + "../../uiresources/app/inspector/inspector_glyph.ui"
    tocpath = maindir + "test2-helptips.yaml"
    jsonpath = maindir + "test2-helptips.json"
    outdir = maindir + "test2-yaml"

    for uipath_ in getUiPaths(path=uipath):
        try:
            uid = UIDoc(
                uipath=uipath_,
                tocpath=tocpath,
                yamldir=outdir,
                logLevel="DEBUG",
                emptytoyaml=True,
            )
            uid.update(
                rebuildStatusTipsInXml=True, replaceToolTipsInXml=True, updateYaml=True
            )
            # Example of how to show the UI
            # uid.prepQtApp()
            # uid.showQtApp()
            # uid.quitQtApp()
        except (FileNotFoundError, ValueError) as e:
            print(f"Error processing {uipath_}: {e}")

    if os.path.exists(outdir):
        # Note: UIBuild accepts (jsonpath, dir, extra=False, logLevel="INFO")
        # and does not take a `tocpath` parameter.
        uib = UIBuild(dir=outdir, jsonpath=jsonpath)
        uib.build()

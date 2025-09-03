#!/usr/bin/env python3
# this_file: src/qtuidoctools/__main__.py
"""
qtuidoctools
------------
Copyright (c) 2019 Adam Twardoch <adam+github@twardoch.com>
MIT license. Python 3.11+.

qtuidoctools update -d PATH_TO_PROTEUS_REPO -t helptips.yaml -o yaml
"""

import sys
from collections import OrderedDict

import fire
from yaplon import oyaml

from . import __version__
from .qtui import UIDoc, getUiPaths
from .qtuibuild import UIBuild


def clipaths(uidir, uipath):
    """Get UI paths from directory or single path."""
    if uidir:
        uipaths = getUiPaths(dir=uidir)
    elif uipath:
        uipaths = getUiPaths(path=uipath)
    else:
        uipaths = []
        sys.stderr.write("-d or -u is required\n")
        sys.exit(2)
    return uipaths


def cleanUpYamlData(data, allowEmpty=True):
    """Clean up YAML data structure."""
    for ctr in data:
        od = data[ctr]
        nd = OrderedDict()
        for k, v in sorted(od.items(), key=lambda t: t[0]):
            if allowEmpty:
                nd[k] = v
            else:
                if v.lstrip().rstrip():
                    nd[k] = v
        data[ctr] = nd
    return data


class QtUIDocTools:
    """
    qtuidoctools

    Update a recursive folder with .ui Qt XML files or single .ui file
    and YAML files, or build the YAML files into a JSON

    For more help type: qtuidoctools update --help

    Update only UI: qtuidoctools update --uidir=UIDIR

    Update UI & YAML: qtuidoctools update --uidir=UIDIR --tocyaml=helptips.yaml --outyamldir=yaml

    Build JSON: qtuidoctools build --json=helptips.json --toc=helptips.yaml --dir=yaml
    """

    def version(self):
        """Show the version and exit."""
        print(f"qtuidoctools, version {__version__}")

    def update(
        self,
        uidir=None,
        uixml=None,
        tocyaml=None,
        outyamldir=None,
        nosavexml=False,
        tooltipstoxml=False,
        tooltipstoyaml=False,
        replaceinyaml=False,
        emptytoyaml=False,
        alwayssaveyaml=False,
        verbose=False,
        quiet=False,
    ):
        """
        -d UIDIR | -u UI -t TOC -o YAMLDIR  (UI file or folder to YAML files)

        Update only UI: qtuidoctools update --uidir=UIDIR

        Update UI & YAML: qtuidoctools update --uidir=UIDIR --tocyaml=helptips.yaml --outyamldir=yaml

        Args:
            uidir: input QtUI recursive dir
            uixml: input QtUI file
            tocyaml: output TOC file
            outyamldir: folder for output YAML files
            nosavexml: do not save the the modified QtUI files
            tooltipstoxml: copy YAML h.tip to QtUI toolTip
            tooltipstoyaml: copy QtUI toolTip to YAML h.tip
            replaceinyaml: replace YAML h.nam (deletes local edits!)
            emptytoyaml: write empty properties to YAML
            alwayssaveyaml: always save YAML
            verbose: print detailed information
            quiet: only print warnings and errors
        """
        if verbose:
            logLevel = "DEBUG"
        elif quiet:
            logLevel = "WARNING"
        else:
            logLevel = "INFO"

        for ui_file_path in clipaths(uidir, uixml):
            uid = UIDoc(
                uipath=ui_file_path,
                tocpath=tocyaml,
                yamldir=outyamldir,
                emptytoyaml=emptytoyaml,
                alwayssaveyaml=alwayssaveyaml,
                logLevel=logLevel,
            )
            if tocyaml:
                uid.updateToc()
            uid.rebuildStatusTipsInXml = True
            if tooltipstoxml:
                uid.replaceToolTipsInXml = True
            if tooltipstoyaml:
                uid.replaceToolTipsInYaml = True
            if outyamldir:
                uid.updateYaml = True
                uid.replaceNamInYaml = replaceinyaml
            uid.updateXmlAndYaml()
            if not nosavexml:
                uid.saveXml()
            if outyamldir:
                uid.saveYaml()
            if tocyaml:
                uid.saveToc()
            if verbose:
                uid.log("updated")

    def cleanup(
        self,
        uidir=None,
        uixml=None,
        tocyaml=None,
        outyamldir=None,
        emptytoyaml=False,
        compactyaml=False,
        verbose=False,
        quiet=False,
    ):
        """
        [-c] [-e] -d UIDIR | -u UI | -t TOC | -o YAMLDIR (do a purely technical refresh of a given component)

        Args:
            uidir: refresh QtUI recursive dir N/A
            uixml: refresh QtUI file N/A
            tocyaml: refresh TOC file
            outyamldir: refresh YAML files in folder
            emptytoyaml: write empty properties to YAML
            compactyaml: write compact
            verbose: print detailed information
            quiet: only print warnings and errors
        """
        bigyaml = not compactyaml

        if uidir or uixml:
            if not quiet:
                print("-u or -d not implemented")
        elif tocyaml:
            with open(tocyaml) as f:
                data = oyaml.read_yaml(f)
            for k in data:
                d = data[k]
                data[k] = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
            yaml = oyaml.yaml_dumps(
                data,
                compact=False,
                width=0,
                quote_strings=bigyaml,
                block_strings=bigyaml,
            )
            with open(tocyaml, "w") as f:
                f.write(yaml)
                if not quiet:
                    print(f"Saved: {tocyaml}")
        elif outyamldir:
            yamlpaths = getUiPaths(path="*.yaml", dir=outyamldir)
            for yamlpath in yamlpaths:
                with open(yamlpath) as f:
                    data = oyaml.read_yaml(f)
                data = cleanUpYamlData(data, allowEmpty=emptytoyaml)
                yaml = oyaml.yaml_dumps(
                    data,
                    compact=False,
                    width=0,
                    quote_strings=bigyaml,
                    block_strings=bigyaml,
                )
                with open(yamlpath, "w") as f:
                    f.write(yaml)
                    if not quiet:
                        print(f"Saved: {yamlpath}")

    def build(
        self,
        json=None,
        toc=None,
        dir=None,
        extra=False,
        verbose=False,
        quiet=False,
    ):
        """
        -j JSON -t TOC -d DIR (YAML files to JSON)

        Build JSON: qtuidoctools build --json=helptips.json --toc=helptips.yaml --dir=yaml

        Args:
            json: output JSON file
            toc: input TOC file
            dir: folder for input YAML files
            extra: append debug info to the help tips
            verbose: print detailed information
            quiet: only print warnings and errors
        """
        if verbose:
            logLevel = "DEBUG"
        elif quiet:
            logLevel = "WARNING"
        else:
            logLevel = "INFO"

        uib = UIBuild(json, dir, extra, logLevel)
        uib.build()


def cli():
    """Main CLI entry point."""
    fire.Fire(QtUIDocTools)


if __name__ == "__main__":
    cli()

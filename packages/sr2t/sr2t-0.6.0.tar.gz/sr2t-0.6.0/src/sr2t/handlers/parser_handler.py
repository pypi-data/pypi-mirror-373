#!/usr/bin/env python3

"""sr2t Parser Handler Module"""

import json
import zipfile

import sr2t.parsers.dirble
import sr2t.parsers.fortify
import sr2t.parsers.nessus
import sr2t.parsers.nikto
import sr2t.parsers.nmap
import sr2t.parsers.testssl
from defusedxml.ElementTree import parse


def handle_nessus(args, workbook):
    """Handle Nessus XML files and parse them into a structured format."""
    data = []
    roots = [parse(file).getroot() for file in args.nessus]
    return sr2t.parsers.nessus.nessus_parser(args, roots, data, workbook)


def handle_nmap(args, workbook):
    """Handle Nmap XML files and parse them into a structured format."""
    roots = [parse(file).getroot() for file in args.nmap]
    return sr2t.parsers.nmap.nmap_parser(args, roots, workbook)


def handle_nikto(args, workbook):
    """Handle Nikto XML files and parse them into a structured format."""
    data = []
    roots = [parse(file).getroot() for file in args.nikto]
    return sr2t.parsers.nikto.nikto_parser(args, roots, data, workbook)


def handle_dirble(args, workbook):
    """Handle Dirble XML files and parse them into a structured format."""
    data = []
    roots = [parse(file).getroot() for file in args.dirble]
    return sr2t.parsers.dirble.dirble_parser(args, roots, data, workbook)


def handle_testssl(args, workbook):
    """Handle testssl.sh XML files and parse them into a structured format."""
    data = []
    roots = [json.load(file) for file in args.testssl]
    return sr2t.parsers.testssl.testssl_parser(args, roots, data, workbook)


def handle_fortify(args, workbook):
    """Handle Fortify XML files and parse them into a structured format."""
    data = []
    roots = []
    for fprfile in args.fortify:
        with zipfile.ZipFile(fprfile.name) as zfpr:
            with zfpr.open("audit.fvdl") as fvdl:
                roots.append(parse(fvdl).getroot())
    return sr2t.parsers.fortify.fortify_parser(args, roots, data, workbook)

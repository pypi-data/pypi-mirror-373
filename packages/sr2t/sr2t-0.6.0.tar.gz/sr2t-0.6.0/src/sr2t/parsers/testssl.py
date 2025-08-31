#!/usr/bin/env python3

"""sr2t testssl.sh parser"""

import csv
import os

from prettytable import PrettyTable
from sr2t.shared.utils import load_yaml


def export_csv(csv_path, headers, rows):
    """Export findings to a CSV file."""
    with open(csv_path, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(rows)


def export_xlsx(workbook, csv_array, header):
    """Export testssl data to XLSX worksheet"""
    bold = workbook.add_format({"bold": True})
    bold.set_text_wrap()
    worksheet_testssl = workbook.add_worksheet("Testssl")
    worksheet_testssl.set_tab_color("green")
    worksheet_testssl.set_column(0, 0, 30)
    tls_bad_cell = workbook.add_format()

    # Dunno why this one doesn't work >:c
    tls_bad_cell.set_align("center")

    tls_bad_cell.set_bg_color("#c00000")
    tls_bad_cell.set_font_color("#ffffff")
    tls_bad_cell.set_border(1)
    tls_bad_cell.set_border_color("#ffffff")
    tls_good_cell = workbook.add_format()

    # Dunno why this one doesn't work >:c
    tls_good_cell.set_align("center")

    tls_good_cell.set_bg_color("#046a38")
    tls_good_cell.set_font_color("#ffffff")
    tls_good_cell.set_border(1)
    tls_good_cell.set_border_color("#ffffff")

    xlsx_header = [{"header_format": bold, "header": f"{title}"} for title in header]
    worksheet_testssl.add_table(
        0,
        0,
        len(csv_array),
        len(csv_array[0]) - 1,
        {
            "data": csv_array,
            "style": "Table Style Light 9",
            "header_row": True,
            "columns": xlsx_header,
        },
    )
    worksheet_testssl.set_row(0, 45)
    worksheet_testssl.set_column(1, len(xlsx_header) - 1, 11)
    worksheet_testssl.conditional_format(
        0,
        1,
        len(csv_array),
        len(csv_array[0]) - 1,
        {"type": "cell", "criteria": "==", "value": '"X"', "format": tls_bad_cell},
    )
    worksheet_testssl.conditional_format(
        0,
        1,
        len(csv_array),
        len(csv_array[0]) - 1,
        {"type": "cell", "criteria": "==", "value": '""', "format": tls_good_cell},
    )
    worksheet_testssl.freeze_panes(0, 1)


def testssl_loopy(hostname, ip, port, entry, data_testssl, testssl_yaml):
    """Process a single scan entry and organize findings by host/port."""
    findings = []

    for section, config in testssl_yaml.items():
        subelements = entry.get(config.get("key"))
        if not isinstance(subelements, list):
            continue

        for subelement in subelements:
            if subelement.get("id") != config.get("id"):
                continue

            value = subelement.get("finding")
            severity = subelement.get("severity")
            expected_value = config.get("expected")
            expected_severity = config.get("severity")
            match_type = config.get("match_type", "equals")

            if value is None or severity is None:
                continue

            # Match severity exactly
            if severity == expected_severity:
                continue

            # Match finding based on match_type
            match = False
            if match_type == "always":
                match = True
            elif match_type == "equals":
                match = value == expected_value
            elif match_type == "contains":
                match = expected_value in value
            elif match_type == "not_equals":
                match = value != expected_value
            elif match_type == "not_contains":
                match = expected_value not in value
            else:
                raise ValueError(f"Unknown match_type: {match_type}")

            if match:
                findings.append(config.get("column"))

    if findings:
        for host, port_, existing_findings in data_testssl:
            if ip == host and port == port_:
                existing_findings.extend(findings)
                break
        else:
            data_testssl.append([hostname, ip, port, findings])


def testssl_parser(args, root, _, workbook):
    """Main parser function for testssl results and output generation."""
    testssl_yaml = load_yaml(None, "sr2t.data", "testssl.yaml")
    data_testssl = []

    # Collect findings
    for host_block in root:
        scan_results = host_block.get("scanResult", [])

        for entry in scan_results:
            is_global_finding = (
                "id" in entry
                and "severity" in entry
                and "finding" in entry
                and "ip" not in entry
                and "port" not in entry
            )
            is_host_block = "targetHost" in entry and "ip" in entry and "port" in entry

            if is_global_finding:
                testssl_loopy(None, None, None, entry, data_testssl, testssl_yaml)
            elif is_host_block:
                testssl_loopy(
                    entry["targetHost"],
                    entry["ip"],
                    entry["port"],
                    entry,
                    data_testssl,
                    testssl_yaml,
                )

    # Prepare output
    unique_vulns = sorted(
        {vuln for _, _, _, findings in data_testssl for vuln in findings}
    )
    headers = ["hostname", "ip address", "port"] + unique_vulns

    table = PrettyTable()
    table.field_names = headers
    table.align["hostname"] = "l"
    table.align["ip address"] = "l"
    table.align["port"] = "l"

    csv_rows = []
    for hostname, ip, port, findings in data_testssl:
        row = [hostname, ip, port] + [
            "X" if vuln in findings else "" for vuln in unique_vulns
        ]
        table.add_row(row)
        csv_rows.append(row)

    # Export CSV if requested
    if args.output_csv:
        csv_path = os.path.splitext(args.output_csv)[0] + "_testssl.csv"
        export_csv(csv_path, headers, csv_rows)

    # Export XLSX if requested
    if args.output_xlsx:
        workbook = export_xlsx(workbook, csv_rows, headers)

    return table, workbook

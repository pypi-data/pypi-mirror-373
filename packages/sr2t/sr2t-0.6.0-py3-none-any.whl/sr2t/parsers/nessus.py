#!/usr/bin/env python3

"""sr2t Nessus parser"""

import csv
import os
import textwrap

from prettytable import PrettyTable
from sr2t.shared.export import export_csv
from sr2t.shared.utils import load_yaml


def extract_nessus_data(var1, reporthost, obs_dict_or_none, var2):
    """
    Generic Nessus loop to extract data based on plugin criteria.

    - If obs_dict_or_none is None: looks for "Nessus SYN scanner" pluginName.
    - If obs_dict_or_none is a dict: matches pluginID keys to extract observations.
    """

    for reportitem in reporthost.findall("ReportItem"):
        plugin_id = int(reportitem.get("pluginID"))

        if obs_dict_or_none is None:
            # Port scan mode
            if reportitem.get("pluginName") == "Nessus SYN scanner":
                if var1 == "addr":
                    var2.append(reporthost.get("name"))
                elif var1 == "port":
                    var2.append(reportitem.get("port"))
        elif plugin_id in obs_dict_or_none:
            # Observation scan mode
            if var1 == "addr":
                var2.append(f"{reporthost.get('name')}:{reportitem.get('port')}")
            elif var1 == "obs":
                var2.append(obs_dict_or_none[plugin_id])


def write_csv_file(base_path, suffix, header, data):
    """Write a CSV file with a given suffix and content."""
    filename = f"{base_path}_{suffix}.csv"
    with open(filename, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for row in data:
            writer.writerow(row)


def build_scan_table(scan_data, observations, label="ip address"):
    """Build PrettyTable and CSV array for a given scan type."""
    table = PrettyTable()
    csv_array = []
    header = [label] + observations
    table.field_names = header
    table.align[label] = "l"
    for ip_address, all_obs in scan_data:
        row = [ip_address]
        row.extend("X" if str(obs) in all_obs else "" for obs in observations)
        table.add_row(row)
        csv_array.append(row)
    return table, csv_array, header


def fill_scan_sheet(
    worksheet,
    csv_array,
    header,
    header_format,
    bad_format,
    good_format,
    row_height=45,
    column_width=11,
):
    if not csv_array:
        return

    xlsx_header = [
        {"header_format": header_format, "header": f"{title}"} for title in header
    ]

    worksheet.add_table(
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
    worksheet.set_row(0, row_height)
    worksheet.set_column(1, len(xlsx_header) - 1, column_width)

    worksheet.conditional_format(
        0,
        1,
        len(csv_array),
        len(csv_array[0]) - 1,
        {
            "type": "cell",
            "criteria": "==",
            "value": '"X"',
            "format": bad_format,
        },
    )
    worksheet.conditional_format(
        0,
        1,
        len(csv_array),
        len(csv_array[0]) - 1,
        {
            "type": "cell",
            "criteria": "==",
            "value": '""',
            "format": good_format,
        },
    )


def write_nessus_xlsx(
    workbook,
    args,
    csv_array,
    main_header,
    scan_types,
    scan_csv_arrays,
    scan_headers,
    autoclassify,
):
    """Write Nessus results to XLSX workbook"""

    def fmt_cell(bg, fg="#ffffff", border=False):
        fmt = workbook.add_format({"text_wrap": True, "bg_color": bg, "font_color": fg})
        if border:
            fmt.set_border(1)
            fmt.set_border_color("#ffffff")
            fmt.set_align("center")
        return fmt

    bold = workbook.add_format({"bold": True, "text_wrap": True})
    wrap = workbook.add_format({"text_wrap": True})
    bad_cell = fmt_cell("#c00000")
    good_cell = fmt_cell("#046a38")
    tls_bad_cell = fmt_cell("#c00000", border=True)
    tls_good_cell = fmt_cell("#046a38", border=True)

    severity_map = {
        "4": {"label": "Critical", "color": "red"},
        "3": {"label": "High", "color": "orange"},
        "2": {"label": "Medium", "color": "yellow"},
        "1": {"label": "Low", "color": "green"},
        "0": {"label": "Info", "color": "blue"},
    }

    worksheet_summary = workbook.add_worksheet("Summary")
    worksheet_summary.write(0, 0, "Summary", bold)
    severity_sheets = {}
    for sev, entry in severity_map.items():
        ws = workbook.add_worksheet(entry["label"])
        ws.set_tab_color(entry["color"])
        ws.set_column(0, 6, 15)
        severity_sheets[sev] = {"worksheet": ws, "row": 1}

    for row in csv_array:
        sev = row[5]
        plugin_id = int(row[2])
        sheet_info = severity_sheets.get(sev)
        if not sheet_info:
            continue
        fmt = (
            bad_cell
            if plugin_id in autoclassify and args.nessus_autoclassify
            else good_cell if sev == "0" else wrap
        )
        ws = sheet_info["worksheet"]
        ws.write_row(sheet_info["row"], 0, row, fmt)
        ws.set_row(sheet_info["row"], 30)
        sheet_info["row"] += 1

    severity_order = sorted(severity_map.keys(), key=int, reverse=True)
    for i, sev in enumerate(severity_order):
        info = severity_sheets[sev]
        ws = info["worksheet"]
        row_count = info["row"] - 1
        if row_count > 0:
            ws.add_table(
                0,
                0,
                row_count,
                6,
                {
                    "style": "Table Style Light 9",
                    "header_row": True,
                    "columns": [
                        {"header_format": bold, "header": h} for h in main_header
                    ],
                },
            )
        ws.set_row(0, 30)
        worksheet_summary.write(i + 1, 0, severity_map[sev]["label"])
        worksheet_summary.write(i + 1, 1, row_count)

    for scan in scan_types:
        key = f"{scan['key']}scan"
        if not scan_csv_arrays[key]:
            continue
        worksheet = workbook.add_worksheet(scan["sheet_name"])
        worksheet.set_tab_color("black")
        worksheet.set_column(0, 0, 20)
        worksheet.write_row(0, 0, scan_headers[key])
        fill_scan_sheet(
            worksheet,
            scan_csv_arrays[key],
            scan_headers[key],
            bold,
            tls_bad_cell,
            tls_good_cell,
        )

    worksheet_portscan = workbook.add_worksheet("SYN")
    worksheet_portscan.set_tab_color("black")
    worksheet_portscan.set_column(0, 0, 15)
    worksheet_portscan.write_row(0, 0, scan_headers["portscan"])
    worksheet_portscan.add_table(
        0,
        0,
        len(scan_csv_arrays["portscan"]),
        len(scan_csv_arrays["portscan"][0]) - 1,
        {
            "data": scan_csv_arrays["portscan"],
            "style": "Table Style Light 9",
            "header_row": True,
            "columns": [
                {"header_format": bold, "header": h} for h in scan_headers["portscan"]
            ],
        },
    )
    worksheet_portscan.freeze_panes(1, 1)


def nessus_parser(args, root, data_nessus, workbook):
    """Nessus parser"""

    # Scan type definitions
    scan_types = [
        {
            "key": "tls",
            "label": "TLS",
            "arg_attr": "nessus_tls_file",
            "filename": "nessus_tls.yaml",
            "sheet_name": "TLS",
        },
        {
            "key": "x509",
            "label": "X.509",
            "arg_attr": "nessus_x509_file",
            "filename": "nessus_x509.yaml",
            "sheet_name": "X.509",
        },
        {
            "key": "http",
            "label": "HTTP",
            "arg_attr": "nessus_http_file",
            "filename": "nessus_http.yaml",
            "sheet_name": "HTTP",
        },
        {
            "key": "smb",
            "label": "SMB",
            "arg_attr": "nessus_smb_file",
            "filename": "nessus_smb.yaml",
            "sheet_name": "SMB",
        },
        {
            "key": "rdp",
            "label": "RDP",
            "arg_attr": "nessus_rdp_file",
            "filename": "nessus_rdp.yaml",
            "sheet_name": "RDP",
        },
        {
            "key": "ssh",
            "label": "SSH",
            "arg_attr": "nessus_ssh_file",
            "filename": "nessus_ssh.yaml",
            "sheet_name": "SSH",
        },
        {
            "key": "snmp",
            "label": "SNMP",
            "arg_attr": "nessus_snmp_file",
            "filename": "nessus_snmp.yaml",
            "sheet_name": "SNMP",
        },
    ]

    # Load observation data
    data_package = "sr2t.data"
    loaded_data = {
        f"{scan['key']}_obs": load_yaml(
            getattr(args, scan["arg_attr"]), data_package, scan["filename"]
        )
        for scan in scan_types
    }
    autoclassify = load_yaml(
        getattr(args, "nessus_autoclassify_file"),
        data_package,
        "nessus_autoclassify.yaml",
    )

    # Define scan configuration
    scan_config = {
        f"{scan['key']}scan": {
            "func": extract_nessus_data,
            "obs": loaded_data[f"{scan['key']}_obs"],
            "modes": ["addr", "obs"],
        }
        for scan in scan_types
    }
    scan_config["portscan"] = {
        "func": extract_nessus_data,
        "obs": None,
        "modes": ["addr", "port"],
    }

    # Parse Nessus XML
    scan_results = {key: [] for key in scan_config}
    for element in root:
        for reporthost in element.findall("Report/ReportHost"):
            for reportitem in reporthost.findall("ReportItem"):
                if int(reportitem.get("severity")) >= args.nessus_min_severity:
                    data_nessus.append(
                        [
                            reporthost.get("name"),
                            reportitem.get("port"),
                            reportitem.get("pluginID"),
                            textwrap.fill(
                                reportitem.get("pluginName"),
                                width=args.nessus_plugin_name_width,
                            ),
                            reportitem.findtext("plugin_output"),
                            reportitem.get("severity"),
                        ]
                    )

            # Porcess scans
            for scan_name, config in scan_config.items():
                addr, obs = [], []
                for mode, target in zip(config["modes"], [addr, obs]):
                    config["func"](mode, reporthost, config["obs"], target)
                if addr:
                    scan_results[scan_name].append([addr[0], obs])

    # Sort scan results
    def sortf(data):
        key_map = {
            "ip-address": 0,
            "port": 1,
            "plugin-id": 2,
            "plugin-name": 3,
            "severity": 4,
        }
        key = key_map.get(args.nessus_sort_by, 0)
        reverse = args.nessus_sort_by == "severity"
        return sorted(data, key=lambda x: x[key], reverse=reverse)

    # Build main Nessus table
    my_nessus_table = PrettyTable()
    main_header = [
        "host",
        "port",
        "plugin id",
        "plugin name",
        "plugin output",
        "severity",
        "annotations".ljust(args.annotation_width),
    ]
    my_nessus_table.field_names = main_header
    for col in main_header:
        my_nessus_table.align[col] = "l"

    csv_array = []
    for row in sortf(data_nessus):
        annotation = autoclassify.get(int(row[2]), {}).get("stdobs_title", "X")
        row.append(annotation)
        my_nessus_table.add_row(row)
        csv_array.append(row)

    # Build tables
    scan_tables, scan_csv_arrays, scan_headers = {}, {}, {}

    for scan in scan_types:
        scan_key = f"{scan['key']}scan"
        scan_data = scan_results[scan_key]
        observations = sorted(set(obs for _, all_obs in scan_data for obs in all_obs))
        table, csv_data, header_row = build_scan_table(scan_data, observations)
        scan_tables[scan_key] = table
        scan_csv_arrays[scan_key] = csv_data
        scan_headers[scan_key] = header_row

    # Handle portscan separately
    ports = sorted(
        set(
            int(port)
            for _, open_ports in scan_results["portscan"]
            for port in open_ports
        )
    )
    table, portscan_csv, header = build_scan_table(
        scan_results["portscan"], [str(p) for p in ports]
    )
    scan_tables["portscan"] = table
    scan_csv_arrays["portscan"] = portscan_csv
    scan_headers["portscan"] = header

    # Write CSV output if requested
    if args.output_csv:
        base = os.path.splitext(args.output_csv)[0]
        severity_map = {
            "4": "critical",
            "3": "high",
            "2": "medium",
            "1": "low",
            "0": "info",
        }

        for sev, label in severity_map.items():
            filtered = [row for row in csv_array if row[5] == sev]
            if filtered:
                export_csv(f"{base}_nessus_{label}.csv", main_header, filtered)

        for scan in scan_types:
            scan_key = f"{scan['key']}scan"
            if scan_key in scan_csv_arrays and scan_csv_arrays[scan_key]:
                export_csv(
                    f"{base}_nessus_{scan['key']}.csv",
                    scan_headers[scan_key],
                    scan_csv_arrays[scan_key],
                )
        export_csv(
            f"{base}_nessus_portscan.csv",
            scan_headers["portscan"],
            scan_csv_arrays["portscan"],
        )

    # Write XLSX output if requested
    if args.output_xlsx:
        write_nessus_xlsx(
            workbook,
            args,
            csv_array,
            main_header,
            scan_types,
            scan_csv_arrays,
            scan_headers,
            autoclassify,
        )

    return (
        my_nessus_table,
        scan_tables["portscan"],
        scan_tables["tlsscan"],
        scan_tables["x509scan"],
        scan_tables["httpscan"],
        scan_tables["smbscan"],
        scan_tables["rdpscan"],
        scan_tables["sshscan"],
        scan_tables["snmpscan"],
        scan_csv_arrays,
        scan_headers,
        workbook,
    )

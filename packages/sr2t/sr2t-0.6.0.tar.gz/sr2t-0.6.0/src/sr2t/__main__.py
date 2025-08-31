#!/usr/bin/env python3

"""sr2t"""

import argparse

import xlsxwriter
from sr2t.handlers.output_handler import (
    any_output_specified,
    print_to_console,
    write_txt_output,
)
from sr2t.handlers.parser_handler import (
    handle_dirble,
    handle_fortify,
    handle_nessus,
    handle_nikto,
    handle_nmap,
    handle_testssl,
)


def get_args():
    """Get arguments"""

    parser = argparse.ArgumentParser(
        description="Converting scanning reports to a tabular format"
    )
    input_group = parser.add_argument_group("specify at least one")
    input_group.add_argument(
        "--nessus",
        type=argparse.FileType("r"),
        nargs="+",
        help="Specify (multiple) Nessus XML files.",
    )
    input_group.add_argument(
        "--nmap",
        type=argparse.FileType("r"),
        nargs="+",
        help="Specify (multiple) Nmap XML files.",
    )
    input_group.add_argument(
        "--nikto",
        type=argparse.FileType("r"),
        nargs="+",
        help="Specify (multiple) Nikto XML files.",
    )
    input_group.add_argument(
        "--dirble",
        type=argparse.FileType("r"),
        nargs="+",
        help="Specify (multiple) Dirble XML files.",
    )
    input_group.add_argument(
        "--testssl",
        type=argparse.FileType("r"),
        nargs="+",
        help="Specify (multiple) Testssl JSON files.",
    )
    input_group.add_argument(
        "--fortify",
        type=argparse.FileType("r"),
        nargs="+",
        help="Specify (multiple) HP Fortify FPR files.",
    )
    parser.add_argument(
        "--nmap-state",
        default="open",
        help="Specify the desired state to filter (e.g. open|filtered).",
    )
    parser.add_argument(
        "--nmap-host-list",
        default=None,
        action="store_true",
        help="Specify to ouput a list of hosts.",
    )
    parser.add_argument(
        "--nmap-services",
        default="store_false",
        action="store_true",
        help="Specify to ouput a supplemental list of detected services.",
    )
    parser.add_argument(
        "--no-nessus-autoclassify",
        default="store_true",
        action="store_false",
        dest="nessus_autoclassify",
        help="Specify to not autoclassify " + "Nessus results.",
    )
    parser.add_argument(
        "--nessus-autoclassify-file",
        type=argparse.FileType("r"),
        help="Specify to override a custom Nessus autoclassify YAML file.",
    )
    parser.add_argument(
        "--nessus-tls-file",
        type=argparse.FileType("r"),
        help="Specify to override a custom Nessus TLS findings YAML file.",
    )
    parser.add_argument(
        "--nessus-x509-file",
        type=argparse.FileType("r"),
        help="Specify to override a custom Nessus X.509 findings YAML file.",
    )
    parser.add_argument(
        "--nessus-http-file",
        type=argparse.FileType("r"),
        help="Specify to override a custom Nessus HTTP findings YAML file.",
    )
    parser.add_argument(
        "--nessus-smb-file",
        type=argparse.FileType("r"),
        help="Specify to override a custom Nessus SMB findings YAML file.",
    )
    parser.add_argument(
        "--nessus-rdp-file",
        type=argparse.FileType("r"),
        help="Specify to override a custom Nessus RDP findings YAML file.",
    )
    parser.add_argument(
        "--nessus-ssh-file",
        type=argparse.FileType("r"),
        help="Specify to override a custom Nessus SSH findings YAML file.",
    )
    parser.add_argument(
        "--nessus-snmp-file",
        type=argparse.FileType("r"),
        help="Specify to override a custom Nessus SNMP findings YAML file.",
    )
    parser.add_argument(
        "--nessus-min-severity",
        default=0,
        type=int,
        help="Specify the minimum severity to output (e.g. 1).",
    )
    parser.add_argument(
        "--nessus-plugin-name-width",
        default=80,
        type=int,
        help="Specify the width of the pluginid column (e.g. 30).",
    )
    parser.add_argument(
        "--nessus-sort-by",
        default="plugin-id",
        help="Specify to sort output by ip-address, port, plugin-id, "
        + "plugin-name or severity.",
    )
    parser.add_argument(
        "--nikto-description-width",
        default=80,
        type=int,
        help="Specify the width of the description column (e.g. 30).",
    )
    parser.add_argument(
        "--fortify-details",
        action="store_true",
        help="Specify to include the Fortify abstracts, explanations and "
        + "recommendations for each vulnerability.",
    )
    parser.add_argument(
        "--annotation-width",
        default=1,
        type=int,
        help="Specify the width of the annotation column (e.g. 30).",
    )
    parser.add_argument(
        "-oC", "--output-csv", help="Specify the output CSV basename (e.g. output)."
    )
    parser.add_argument(
        "-oT", "--output-txt", help="Specify the output TXT file (e.g. output.txt)."
    )
    parser.add_argument(
        "-oX",
        "--output-xlsx",
        help="Specify the output XLSX file (e.g. output.xlsx). Only for "
        + "Nessus at the moment",
    )
    parser.add_argument(
        "-oA",
        "--output-all",
        help="Specify the output basename to output to all formats (e.g. output).",
    )

    args = parser.parse_args()
    if not any(
        [args.nessus, args.nmap, args.nikto, args.dirble, args.testssl, args.fortify]
    ):
        parser.error(
            "at least one of the arguments --nessus --nmap --nikto --dirble"
            + "--testssl --fortify is required"
        )

    return parser.parse_args()


def init_workbook(args):
    """Initialize the workbook for XLSX output"""
    if args.output_all:
        args.output_csv = args.output_all
        args.output_txt = args.output_all + ".txt"
        args.output_xlsx = args.output_all + ".xlsx"
    return (
        xlsxwriter.Workbook(
            args.output_xlsx, {"strings_to_urls": False, "remove_timezone": True}
        )
        if args.output_xlsx
        else None
    )


def main():
    """Main function"""

    args = get_args()
    get_args()
    workbook = init_workbook(args)
    tables = {}

    if args.nessus:
        (
            tables["nessus"],
            tables["nessus_portscan"],
            tables["nessus_tls"],
            tables["nessus_x509"],
            tables["nessus_http"],
            tables["nessus_smb"],
            tables["nessus_rdp"],
            tables["nessus_ssh"],
            tables["nessus_snmp"],
            _,
            _,
            workbook,
        ) = handle_nessus(args, workbook)

    if args.nmap:
        (
            tables["nmap_tcp"],
            tables["nmap_udp"],
            tables["nmap_services"],
            tables["nmap_hosts_tcp"],
            tables["nmap_hosts_udp"],
            tables["nmap_ssh_algorithms"],
            tables["nmap_rdp_algorithms"],
            tables["nmap_ssl_algorithms"],
            tables["nmap_http_algorithms"],
            workbook,
        ) = handle_nmap(args, workbook)

    if args.nikto:
        tables["nikto"], _, _, workbook = handle_nikto(args, workbook)

    if args.dirble:
        tables["dirble"], _, _, workbook = handle_dirble(args, workbook)

    if args.testssl:
        tables["testssl"], workbook = handle_testssl(args, workbook)

    if args.fortify:
        tables["fortify"], _, _, workbook = handle_fortify(args, workbook)

    if args.output_txt:
        write_txt_output(args, tables)
    elif not any_output_specified(args):
        print_to_console(args, tables)

    if workbook:
        workbook.close()


if __name__ == "__main__":
    main()

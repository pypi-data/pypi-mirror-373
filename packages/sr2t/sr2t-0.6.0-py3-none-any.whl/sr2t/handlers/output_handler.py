#!/usr/bin/env python3

"""sr2t Output Handler Module"""


def write_txt_output(args, tables):
    """Write output to a text file."""
    with open(args.output_txt, "w", encoding="utf-8") as txtfile:
        for name, content in tables.items():
            if isinstance(content, dict):
                for label, table in content.items():
                    if table:
                        print(f"{label}:", file=txtfile)
                        print(table, "\n", file=txtfile)
            else:
                print(content, "\n", file=txtfile)


def print_to_console(args, tables):
    """Print output to the console."""
    for label, table in tables.items():
        if not table:
            continue
        if isinstance(table, dict):
            for sublabel, subtable in table.items():
                if table:
                    print(f"{sublabel}:")
                    print(subtable, "\n")
        else:
            print(f"{label}:")
            print(table, "\n")


def any_output_specified(args):
    """Check if any output format is specified."""
    return any([args.output_csv, args.output_txt, args.output_xlsx, args.output_all])

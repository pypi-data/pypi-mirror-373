#!/usr/bin/env python3

"""sr2t Nikto parser"""

import csv
import os
import textwrap

from prettytable import PrettyTable


def nikto_parser(args, root, data_nikto, workbook):
    """Nikto parser"""

    for element in root:
        for scandetails in element.findall("niktoscan/scandetails"):
            for item in scandetails.findall("item"):
                list_item = []
                list_item.append(
                    textwrap.fill(
                        item.findtext("description"), width=args.nikto_description_width
                    )
                )
                data_nikto.append(
                    [
                        scandetails.get("targetip"),
                        scandetails.get("targethostname"),
                        scandetails.get("targetport"),
                        list_item,
                    ]
                )

    my_table = PrettyTable()
    csv_array = []
    header = ["target ip", "target hostname", "target port", "description"]
    header.extend(["annotations".ljust(args.annotation_width)])
    my_table.field_names = header
    for targetip, targethostname, targetport, item in data_nikto:
        row = [targetip, targethostname, targetport, item[0]]
        row.extend(["X"])
        my_table.add_row(row)
        csv_array.append(row)
    my_table.align["target ip"] = "l"
    my_table.align["target hostname"] = "l"
    my_table.align["target port"] = "l"
    my_table.align["description"] = "l"

    if args.output_csv:
        with open(os.path.splitext(args.output_csv)[0] + "_nikto.csv", "w") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header)
            for row in csv_array:
                csvwriter.writerow(row)

    if args.output_xlsx:
        bold = workbook.add_format({"bold": True})
        bold.set_text_wrap()
        worksheet_nikto = workbook.add_worksheet("Nikto")
        worksheet_nikto.set_tab_color("red")
        worksheet_nikto.set_column(0, 0, 18)
        worksheet_nikto.set_column(1, 1, 18)
        worksheet_nikto.set_column(2, 2, 12)
        worksheet_nikto.set_column(3, 3, 75)
        worksheet_nikto.set_column(4, 4, 20)
        xlsx_header = [
            {"header_format": bold, "header": "{}".format(title)} for title in header
        ]
        worksheet_nikto.add_table(
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
        worksheet_nikto.freeze_panes(0, 1)

    return my_table, csv_array, header, workbook

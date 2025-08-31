#!/usr/bin/env python3

"""sr2t Dirble parser"""

import csv
import os

from prettytable import PrettyTable


def dirble_parser(args, root, data_dirble, workbook):
    """Dirble parser"""

    for element in root:
        for path in element.findall("path"):
            list_file = []
            list_file.append(path.get("code"))
            list_file.append(path.get("content_len"))
            list_file.append(path.get("is_directory"))
            list_file.append(path.get("is_listable"))
            list_file.append(path.get("found_from_listable"))
            list_file.append(path.get("redirect_url"))
            data_dirble.append([path.get("url"), list_file])

    my_dirble_table = PrettyTable()
    csv_array = []
    header = [
        "url",
        "code",
        "content len",
        "is directory",
        "is listable",
        "found from listable",
    ]
    header.extend(["redirect url", "annotations".ljust(args.annotation_width)])
    my_dirble_table.field_names = header
    for url, item in data_dirble:
        row = [url, item[0], item[1], item[2], item[3], item[4], item[5]]
        row.extend(["X"])
        my_dirble_table.add_row(row)
        csv_array.append(row)
    my_dirble_table.align["url"] = "l"
    my_dirble_table.align["content len"] = "l"
    my_dirble_table.align["is directory"] = "l"
    my_dirble_table.align["is listable"] = "l"
    my_dirble_table.align["found from listable"] = "l"
    my_dirble_table.align["redirect url"] = "l"

    if args.output_csv:
        with open(os.path.splitext(args.output_csv)[0] + "_dirble.csv", "w") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header)
            for row in csv_array:
                csvwriter.writerow(row)

    if args.output_xlsx:
        bold = workbook.add_format({"bold": True})
        wrap = workbook.add_format()
        wrap.set_text_wrap()
        worksheet_dirble = workbook.add_worksheet("Dirble")
        worksheet_dirble.set_tab_color("blue")
        worksheet_dirble.set_column(0, 0, 60)
        worksheet_dirble.set_column(2, 2, 12)
        worksheet_dirble.set_column(3, 3, 12)
        worksheet_dirble.set_column(4, 4, 12)
        worksheet_dirble.set_column(5, 5, 20)
        worksheet_dirble.set_column(6, 6, 60)
        worksheet_dirble.set_column(7, 7, 20)
        xlsx_header = [
            {"header_format": bold, "header": f"{title}"} for title in header
        ]
        worksheet_dirble.add_table(
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
        worksheet_dirble.freeze_panes(0, 1)

    return my_dirble_table, csv_array, header, workbook

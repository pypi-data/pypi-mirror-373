#!/usr/bin/env python3

"""sr2t Fortify parser"""

import csv
import os

from prettytable import PrettyTable


def fortify_parser(args, root, data_fortify, workbook):
    """HP Fortify parser"""

    namespace = {"fvdl": "xmlns://www.fortifysoftware.com/schema/fvdl"}
    dict_abstract = dict()
    dict_explanation = dict()
    dict_recommendation = dict()
    for element in root:
        for vuln in element.findall(
            "fvdl:Vulnerabilities/fvdl:Vulnerability", namespace
        ):
            for snippet in vuln.findall(
                "fvdl:AnalysisInfo/fvdl:Unified/fvdl:Trace/fvdl:Primary/"
                "fvdl:Entry/fvdl:Node/fvdl:SourceLocation",
                namespace,
            ):
                var_snippet = snippet.get("snippet")
            for classid in vuln.findall("fvdl:ClassInfo/fvdl:ClassID", namespace):
                var_classid = classid.text
            for type in vuln.findall("fvdl:ClassInfo/fvdl:Type", namespace):
                var_type = type.text
            for subtype in vuln.findall("fvdl:ClassInfo/fvdl:Subtype", namespace):
                var_subtype = subtype.text
            for severity in vuln.findall(
                "fvdl:InstanceInfo/fvdl:InstanceSeverity", namespace
            ):
                var_severity = severity.text
            for confidence in vuln.findall(
                "fvdl:InstanceInfo/fvdl:Confidence", namespace
            ):
                var_confidence = confidence.text
            if not args.fortify_details:
                data_fortify.append(
                    [var_snippet, var_type, var_subtype, var_severity, var_confidence]
                )
            elif args.fortify_details:
                data_fortify.append(
                    [
                        var_snippet,
                        var_type,
                        var_subtype,
                        var_severity,
                        var_confidence,
                        var_classid,
                        var_classid,
                        var_classid,
                    ]
                )
        for description_classid in element.findall("fvdl:Description", namespace):
            var_desciprion_classid = description_classid.get("classID")
            for abstract in description_classid.findall("fvdl:Abstract", namespace):
                dict_abstract[var_desciprion_classid] = abstract.text
            for explanation in description_classid.findall(
                "fvdl:Explanation", namespace
            ):
                dict_explanation[var_desciprion_classid] = explanation.text
            for recommendation in description_classid.findall(
                "fvdl:Recommendations", namespace
            ):
                dict_recommendation[var_desciprion_classid] = recommendation.text

    my_table = PrettyTable()
    csv_array = []
    header = ["source location", "type", "subtype", "severity", "confidence"]
    if args.fortify_details:
        header.extend(["abstract"])
        header.extend(["explanation"])
        header.extend(["recommendation"])
    header.extend(["annotations".ljust(args.annotation_width)])
    my_table.field_names = header
    for row in data_fortify:
        if args.fortify_details:
            row[5] = dict_abstract.get(row[5])
            row[6] = dict_explanation.get(row[6])
            row[7] = dict_recommendation.get(row[7])
        row.extend(["X"])
        my_table.add_row(row)
        csv_array.append(row)
    my_table.align["source location"] = "l"
    my_table.align["type"] = "l"
    my_table.align["subtype"] = "l"

    if args.output_csv:
        with open(
            os.path.splitext(args.output_csv)[0] + "_fortify.csv", "w"
        ) as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header)
            for row in csv_array:
                csvwriter.writerow(row)

    if args.output_xlsx:
        bold = workbook.add_format({"bold": True})
        bold.set_text_wrap()
        wrap = workbook.add_format()
        wrap.set_text_wrap()
        worksheet_fortify = workbook.add_worksheet("Fortify")
        worksheet_fortify.set_tab_color("orange")
        worksheet_fortify.set_column(0, 0, 80)
        worksheet_fortify.set_column(1, 1, 25)
        worksheet_fortify.set_column(2, 2, 35)
        worksheet_fortify.set_column(3, 3, 12)
        worksheet_fortify.set_column(4, 4, 12)
        worksheet_fortify.set_column(5, 5, 20)
        worksheet_fortify.set_column(6, 6, 20)
        xlsx_header = [
            {"header_format": bold, "header": "{}".format(title)} for title in header
        ]
        worksheet_fortify.add_table(
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
        row = 1
        while row <= len(csv_array):
            worksheet_fortify.set_row(row, 30, wrap)
            row += 1
        worksheet_fortify.freeze_panes(0, 1)

    return my_table, csv_array, header, workbook

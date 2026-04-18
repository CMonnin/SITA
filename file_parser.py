import csv

import pandas as pd

import SITA_module


def process_csv(file_path):
    """Read a CSV with columns: name, formula, backbone_c (plus header row).
    Returns {name: correction_matrix (list-of-lists)}.
    """
    output_dict = {}
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        for line_counter, row in enumerate(reader):
            if line_counter == 0:
                continue
            name = row[0]
            molecular_formula = row[1]
            backbone_c = int(row[2])
            output_dict[name] = (
                SITA_module.LabelledCompound(
                    formula=molecular_formula,
                    labelled_element="C",
                    backbone_c=backbone_c,
                )
                .correction_matrix()
                .tolist()
            )
    print(output_dict)
    return output_dict


def csv_to_xlsx_for_download(a_dict, output_path="output.xlsx"):
    """Write one sheet per compound into a single .xlsx workbook."""
    with pd.ExcelWriter(output_path, mode="w") as writer:
        for sheet_name, matrix in a_dict.items():
            pd.DataFrame(matrix).to_excel(
                writer, sheet_name=sheet_name, header=False, index=False
            )

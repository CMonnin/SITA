"""Batch CLI: read a CSV of compounds, produce an xlsx workbook."""

import argparse
import csv
import sys

import pandas as pd

from sita_core import LabelledCompound


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
                LabelledCompound(
                    formula=molecular_formula,
                    labelled_element="C",
                    backbone_c=backbone_c,
                )
                .correction_matrix()
                .tolist()
            )
    return output_dict


def csv_to_xlsx(a_dict, output_path="output.xlsx"):
    """Write one sheet per compound into a single .xlsx workbook."""
    with pd.ExcelWriter(output_path, mode="w") as writer:
        for sheet_name, matrix in a_dict.items():
            pd.DataFrame(matrix).to_excel(
                writer, sheet_name=sheet_name, header=False, index=False
            )


def main():
    parser = argparse.ArgumentParser(
        description="Batch natural-abundance correction matrix generation."
    )
    parser.add_argument(
        "input",
        help="Path to input CSV with columns: name, formula, backbone_c",
    )
    parser.add_argument(
        "-o", "--output",
        default="output.xlsx",
        help="Output xlsx path (default: output.xlsx)",
    )
    args = parser.parse_args()

    result = process_csv(args.input)
    csv_to_xlsx(result, output_path=args.output)
    print(f"Wrote {len(result)} compounds to {args.output}")


if __name__ == "__main__":
    main()

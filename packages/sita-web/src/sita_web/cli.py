"""Batch CLI: read a CSV of compounds, produce an xlsx workbook."""

import argparse
import csv
import re

import pandas as pd

from sita_core import LabelledCompound

_XLSX_FORBIDDEN = re.compile(r"[:\\/?*\[\]]")


def _sanitize_sheet_name(name: str, used: set[str]) -> str:
    cleaned = _XLSX_FORBIDDEN.sub("_", name).strip()[:31] or "sheet"
    candidate, n = cleaned, 1
    while candidate in used:
        suffix = f"_{n}"
        candidate = cleaned[: 31 - len(suffix)] + suffix
        n += 1
    used.add(candidate)
    return candidate


def process_csv(file_path):
    """Read a CSV with columns: name, formula, backbone_c (plus header row).

    Returns {name: correction_matrix (list-of-lists)}.
    """
    output_dict = {}
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        for line_no, row in enumerate(reader, start=1):
            if line_no == 1:
                continue
            if len(row) < 3:
                raise ValueError(
                    f"{file_path}:{line_no}: expected columns name,formula,backbone_c "
                    f"(got {len(row)})"
                )
            name, molecular_formula, backbone_raw = row[0], row[1], row[2]
            try:
                backbone_c = int(backbone_raw)
            except ValueError as e:
                raise ValueError(
                    f"{file_path}:{line_no}: backbone_c={backbone_raw!r} is not an int"
                ) from e
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
    used: set[str] = set()
    with pd.ExcelWriter(output_path, mode="w") as writer:
        for raw_name, matrix in a_dict.items():
            sheet = _sanitize_sheet_name(raw_name, used)
            pd.DataFrame(matrix).to_excel(
                writer, sheet_name=sheet, header=False, index=False
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

import pandas as pd

import SITA_module

import csv


def process_csv(file_path):
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        line_counter = 0
        output_dict = {}
        for row in reader:
            if line_counter != 0:
                molecular_formula_input = row[1]
                vector_size = int(row[2])
                output_dict.update(
                    {
                        row[0]: (
                            SITA_module.LabelledCompound(
                                formula=molecular_formula_input,
                                labelled_element="C",
                                vector_size=vector_size,
                            )
                            .correction_matrix()
                            .tolist()
                        )
                    }
                )

            line_counter += 1

        print(output_dict)
        return output_dict


def csv_to_xlsx_for_download(a_dict):
    df = pd.DataFrame.from_dict(a_dict)
    print(df)
    for index, row in df.iterrows():
        sheet_name = row[0]
        content = pd.DataFrame(row[1])

        with pd.ExcelWriter("output.xlsx", mode="w") as writer:
            content.to_excel(writer, sheet_name=sheet_name, header=False, index=False)

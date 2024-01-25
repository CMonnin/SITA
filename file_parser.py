import pandas as pd


def csv_parser(csv):
    df = pd.read_csv(csv)
    output_list = []

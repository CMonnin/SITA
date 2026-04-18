import file_parser


def main():
    file_parser.csv_to_xlsx_for_download(file_parser.process_csv("template.csv"))


if __name__ == "__main__":
    main()

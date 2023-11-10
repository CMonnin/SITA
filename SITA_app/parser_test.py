import re
from collections import Counter


def formula_parser(formula):
    """
    This function parses the molecular formula
    """
    formula = formula
    # Make two capture groups:
    # 1st one upper case letter lower case letter,
    # 2nd group the digits following the 1st group
    pattern = r"([A-Z][a-z]*)(\d*)"
    groups = re.findall(pattern, formula)
    # creating a dict of hashable objects, the elements and their counts
    elements = Counter()

    for element, count in groups:
        # if count is empty e.g. mol formula: CO, assume 1
        if count == "":
            count = 1
        else:
            count = int(count)

        elements[element] += count

    return elements


if __name__ == "__main__":
    formula = "C3H7NO2"

    parsed = formula_parser(formula)
    print(parsed)
    print(parsed.get("C"))

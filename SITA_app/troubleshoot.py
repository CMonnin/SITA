import itertools


def combo_solver(number_of_isotopes: int, number_of_atoms: int):
    # figures out all the combinations depening on the
    # number of atoms and isotpes of an element
    # eg for the carbon in alanine C3H7NO2 there will be two isotopes
    # and three carbons
    combinations = itertools.combinations_with_replacement(
        range(number_of_isotopes), number_of_atoms
    )
    return list(combinations)


def valid_combos(target: int, combinations: list):
    # a valid combo being one that sums up to the target eg M+0 has a sum
    # of 0, M+1 a sum of 1 etc ...
    valid_combos = [combo for combo in combinations if sum(combo) == target]
    return valid_combos


if __name__ == "__main__":
    combo = combo_solver(2, 3)
    print(combo)
    for i in range(3):
        print(i)
        print(valid_combos(i, combo))

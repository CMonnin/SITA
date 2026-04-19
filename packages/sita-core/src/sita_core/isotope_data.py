"""Natural isotope abundances for common elements.

Source:
    Coursey, J. S., et al. "Atomic weights and isotopic compositions with
    relative atomic masses." NIST Physical Measurement Laboratory (2015).
    https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl

Some isotopes at 0% abundance are included for ease of logic later on.
"""

ISOTOPE_ABUNDANCE_DICT_UNIT_MASS = {
    "H": {"abundance": (0.999885, 0.000115), "mass": (1, 2)},
    "C": {"abundance": (0.9893, 0.0107), "mass": (12, 13)},
    "N": {"abundance": (0.99636, 0.00364), "mass": (14, 15)},
    "O": {"abundance": (0.99757, 0.00038, 0.00205), "mass": (16, 17, 18)},
    "Si": {"abundance": (0.92223, 0.04685, 0.03092), "mass": (28, 29, 30)},
    "P": {"abundance": (1,), "mass": (31,)},
    "S": {
        "abundance": (0.9499, 0.0075, 0.0425, 0, 0.0001),
        "mass": (32, 33, 34, 35, 36),
    },
    "Cl": {"abundance": (0.7576, 0, 0.2424), "mass": (35, 36, 37)},
    "Br": {"abundance": (0.5069, 0, 0.4931), "mass": (79, 80, 81)},
}

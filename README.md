# SITA

Natural-abundance correction for GC-MS mass distribution vectors (MDVs) from
13C stable-isotope tracer experiments. Math follows Fischer & Zamboni,
*Determination of metabolic flux ratios from 13C-experiments and
gas chromatography-mass spectrometry data: protocol and principles*,
Metabolomics: Methods and Protocols (2007).

## backbone_c

Every compound requires a `backbone_c` argument: the number of carbons in the
fragment that are **subject to 13C labelling** in the tracer experiment. These
positions are excluded from the natural-abundance correction because their
labelling IS the measurement signal.

Example: alanine M-57 is the fragment `C8H23NO2Si2`. Eight total carbons, but
only three originate from alanine — the other five come from the TBDMS
derivatizing reagent. So `backbone_c=3`. The MDV length defaults to
`backbone_c + 1` (i.e. M+0 through M+3).

## CSV batch

Run `python parser_test.py` with `template.csv` in the working directory.
CSV columns: `name, formula, backbone_c` (one header row). Output is
`output.xlsx` with one sheet per compound.

## Dash app

`python app.py` — UI has two sections: correction matrix from formula +
backbone_c, and corrected MDV from formula + backbone_c + observed MDV.

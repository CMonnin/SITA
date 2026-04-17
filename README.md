# SITA

Natural-abundance correction for GC-MS mass distribution vectors (MDVs) from
13C stable-isotope tracer experiments.

## References

The mathematical basis follows:

- Nanchen, A., Fuhrer, T., Sauer, U. (2007). *Determination of Metabolic Flux
  Ratios From 13C-Experiments and Gas Chromatography-Mass Spectrometry Data:
  Protocol and Principles.* In: Metabolomics (Methods in Molecular Biology
  358), Humana Press, pp. 177-197.
  doi:[10.1007/978-1-59745-244-1_11](https://doi.org/10.1007/978-1-59745-244-1_11)

- Fischer, E., Zamboni, N., Sauer, U. (2004). *High-throughput metabolic flux
  analysis based on gas chromatography-mass spectrometry derived 13C
  constraints.* Analytical Biochemistry 325(2):308-316.
  doi:[10.1016/j.ab.2003.10.036](https://doi.org/10.1016/j.ab.2003.10.036)

The correction matrix and worked example pinned in `test.py` come from
Nanchen 2007, §3.7 (alanine M-57 fragment).

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

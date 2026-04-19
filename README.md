# SITA

Natural-abundance correction for GC-MS mass distribution vectors (MDVs) from
13C stable-isotope tracer experiments. Given a fragment's molecular formula
and its labelled-backbone carbon count, SITA returns the natural-abundance
correction matrix and the corrected MDV\*.

A live version is hosted at
[sita-app.up.railway.app](https://sita-app.up.railway.app/).

## Project structure

This repo is a [UV workspace](https://docs.astral.sh/uv/concepts/workspaces/) with two packages:

- **`sita-core`** — pure algorithm library (numpy only). The `LabelledCompound` class and isotope data.
- **`sita-web`** — Flask web UI, REST API. Depends on `sita-core`.

## Quick start

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/CMonnin/SITA.git
cd SITA
uv sync
uv run python -m sita_web.app
```

Then open http://127.0.0.1:5000.

## Usage

The web UI has two sections:

1. **Correction matrix** — enter a molecular formula and the number of
   backbone carbons; returns the natural-abundance correction matrix.
2. **Corrected MDV (MDV\*)** — additionally enter a measured MDV; returns
   the natural-abundance-corrected MDV.

### `backbone_c`

Every compound requires a `backbone_c` argument: the number of carbons in
the fragment that are **subject to 13C labelling** in the tracer experiment.
These positions are excluded from the natural-abundance correction because
their labelling is the measurement signal (per Fischer & Zamboni 2004).

Example: alanine M-57 is the fragment `C11H26NO2Si2` (Nanchen 2007 Table 1,
mass 260). Eleven total carbons — three from the alanine backbone, eight
from the two TBDMS groups after loss of the tert-butyl (C4H9). So
`backbone_c=3`. The MDV length defaults to `backbone_c + 1` (M+0 ... M+n).

### Running tests

```bash
uv run pytest
```

### Using the core library programmatically

```python
from sita_core import LabelledCompound

compound = LabelledCompound(
    formula="C11H26NO2Si2",
    labelled_element="C",
    backbone_c=3,
)
matrix = compound.correction_matrix()
```

## Tech stack

- **sita-core**: Python + numpy for the correction math
- **sita-web**: Flask serving a vanilla-JS frontend
- Deployed on Railway

## Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19647450.svg)](https://doi.org/10.5281/zenodo.19647450)

## References

The mathematical basis follows:

- Nanchen, A., Fuhrer, T., Sauer, U. (2007). _Determination of Metabolic
  Flux Ratios From 13C-Experiments and Gas Chromatography-Mass Spectrometry
  Data: Protocol and Principles._ In: Metabolomics (Methods in Molecular
  Biology 358), Humana Press, pp. 177-197.
  doi:[10.1007/978-1-59745-244-1_11](https://doi.org/10.1007/978-1-59745-244-1_11)
- Fischer, E., Zamboni, N., Sauer, U. (2004). _High-throughput metabolic
  flux analysis based on gas chromatography-mass spectrometry derived 13C
  constraints._ Analytical Biochemistry 325(2):308-316.
  doi:[10.1016/j.ab.2003.10.036](https://doi.org/10.1016/j.ab.2003.10.036)

Natural isotope abundances are from Coursey, J. S., et al. _Atomic weights
and isotopic compositions with relative atomic masses._ NIST Physical
Measurement Laboratory (2015).
[physics.nist.gov](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl)

The correction matrix and worked example in the test suite come from
Nanchen 2007, §3.7 (alanine M-57 fragment).

## Contributing

This is an open-source project — contributions are welcome. Fork the repo,
make changes, and open a pull request. For feature requests or bug reports,
open an issue or reach out at `cianmonnin at gmail dot com`.

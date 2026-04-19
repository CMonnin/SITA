# sita-core

Natural-abundance correction for GC-MS mass distribution vectors from 13C stable-isotope tracer experiments.

Pure-Python library implementing the corrections described in Nanchen, Fuhrer
& Sauer (2007) *Determination of Metabolic Flux Ratios From 13C-Experiments
and Gas Chromatography–Mass Spectrometry Data*, Methods in Molecular Biology 358.

## Install

```
pip install sita-core
```

## Usage

```python
from sita_core import LabelledCompound

ala = LabelledCompound(
    formula="C11H26NO2Si2",
    labelled_element="C",
    backbone_c=3,
    mdv_a=[0.6228, 0.1517, 0.0749, 0.1507],
)
corr = ala.correction_matrix()
mdv_star = ala.mdv_star()
```

See the [project repository](https://github.com/CMonnin/SITA) for the full
documentation, CLI, and Flask UI.

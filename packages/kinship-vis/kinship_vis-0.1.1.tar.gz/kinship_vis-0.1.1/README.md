# kinship-vis

Visualize pairwise kinship from **PLINK** `.genome` or **KING** `.kin0` as connected components, with
- **Static images** (PNG/TIFF/JPEG, Matplotlib): edges colored by relationship class, nodes filled by **MT** haplogroup and outlined by **Y** haplogroup.
- **Interactive HTML** (Plotly): the same color scheme with hover tooltips and an optional legend.

> Designed for quick QC and teaching. Works with projects like 1000 Genomes and your own pipelines (PLINK/KING).

---

## Installation

### 1) PyPI (recommended)
```bash
pip install kinship-vis
```

### 2) From GitHub (latest main)
```bash
pip install "git+https://github.com/YOUR_GITHUB_USERNAME/kinship-vis.git"
```

### 3) Conda (Bioconda)
Once the recipe is merged to **bioconda**, you’ll be able to do:
```bash
conda install -c conda-forge -c bioconda kinship-vis
```

**Python/NumPy note:** until the scientific Python stack fully supports NumPy 2, this package pins `numpy<2` to avoid ABI issues.

---

## Command-line usage

Basic help:
```bash
kinship-vis -h
```

Key inputs:
- **Pairs table**: PLINK `.genome` (`IID1 IID2 PI_HAT [Z1]`) **or** KING `.kin0` (`ID1 ID2 Kinship`).
- **Haplogroups** (optional): two-column text files without header: `<sample><tab><haplogroup>`
  - `--haplogroup-Y` — Y haplogroups (node *border* color)
  - `--haplogroup-MT` — MT haplogroups (node *fill* color)
- **Samplesheet** (optional): TSV/CSV/whitespace-delimited, must contain `sample_id`; you can select a label column via `--label-col`.

Important thresholds (defaults):
- `--threshold1 0.75` (close relatives)
- `--threshold2 0.40` (distant relatives)
- `--z1-threshold 0.75`
- `--drop-below-threshold2` — drop edges with `PI_HAT<threshold2` to reduce noise.

Outputs:
- Static **PNG/TIFF/JPEG**: `<prefix>_component_<N>.<ext>`
- Interactive **HTML**: `<prefix>_component_<N>.html`

---

## Examples (using the files in `examples/`)

**KING `.kin0` → separate output folder:**
```bash
kinship-vis G1000_31S.kin0   --haplogroup-Y  G1000_31S_chrY.hapresult.hg   --haplogroup-MT G1000_31S_chrMT_haplogrep.txt   --output kin0/kinship --legend --drop-below-threshold2
```

**PLINK `.genome` → separate output folder:**
```bash
kinship-vis G1000_31S.genome   --haplogroup-Y  G1000_31S_chrY.hapresult.hg   --haplogroup-MT G1000_31S_chrMT_haplogrep.txt   --output genome/kinship --legend --drop-below-threshold2
```

Tip: pre-create the output directories if needed:
```bash
mkdir -p kin0 genome
```

---

## Minimal, reproducible example
```bash
# Create a tiny demo of two related pairs
cat > demo.genome <<EOF
IID1 IID2 PI_HAT Z1
A    B    0.90   0.95
A    C    0.45   0.80
D    E    0.10   0.00
EOF

echo -e "A	R1a" > y.tsv
echo -e "B	R1a" >> y.tsv
echo -e "A	H"   > mt.tsv
echo -e "B	H"   >> mt.tsv

kinship-vis demo.genome --haplogroup-Y y.tsv --haplogroup-MT mt.tsv --output demo/out --legend
```

---

## API (Python)
```python
import pandas as pd
from kinship_vis.io import read_pairs_table
from kinship_vis.graph import build_graph

df = read_pairs_table("your.genome")        # or .kin0
G = build_graph(df, threshold1=0.75)
```

---

## Citation
- **PLINK**: Purcell et al. (2007) *Am J Hum Genet.*
- **KING**: Manichaikul et al. (2010) *Bioinformatics.*

## License
MIT


from __future__ import annotations
import argparse
import sys
import networkx as nx
from .io import read_pairs_table, read_haplogroups, read_samplesheet
from .graph import build_graph
from .viz import assign_colors, plot_static, plot_html

def _cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("genome_file", help="PLINK *.genome or KING *.kin0")
    p.add_argument("--output", default="kinship_graph", help="output file prefix (without extension)")
    p.add_argument(
        "--samplesheet",
        help="Sample sheet (TSV/CSV/whitespace; delimiter auto-detected) with required column: sample_id",
    )
    p.add_argument("--label-col", help="column name to use for node labels (defaults to sample_id)")
    p.add_argument("--haplogroup-Y",  dest="hg_y")
    p.add_argument("--haplogroup-MT", dest="hg_mt")

    # rendering options
    p.add_argument("--dpi",        type=int,   default=150)
    p.add_argument("--figsize",    nargs=2,    type=float, default=[10,8])
    p.add_argument("--node-size",  type=int,   default=500, help="PNG/TIFF node size")
    p.add_argument("-N","--node-size-html", type=int, default=12, help="HTML node size")
    p.add_argument("--edge-width", type=float, default=2)
    p.add_argument("--format", choices=["png","tiff","jpeg"], default="png")
    p.add_argument("--legend", action="store_true")

    # filters
    p.add_argument("--threshold1", type=float, default=0.75)
    p.add_argument("--threshold2", type=float, default=0.40)
    p.add_argument("--z1-threshold", type=float, default=0.75)
    p.add_argument("--max-degree-fraction", type=float)
    p.add_argument("--drop-below-threshold2", action="store_true",
                   help="drop edges with PI_HAT<threshold2 to reduce noise")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()

def main():
    a = _cli()
    try:
        df = read_pairs_table(a.genome_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    G = build_graph(df, a.threshold1, a.threshold2, a.z1_threshold,
                    a.max_degree_fraction, a.drop_below_threshold2, a.verbose)
    if G.number_of_edges() == 0:
        print("[warn] graph empty after filtering"); return

    if a.samplesheet:
        sm = read_samplesheet(a.samplesheet)
        col = a.label_col if (a.label_col and a.label_col in sm.columns) else "sample_id"
        nx.set_node_attributes(G, sm.set_index("sample_id")[col].to_dict(), "label")

    hgY  = read_haplogroups(a.hg_y)  if a.hg_y  else None
    hgMT = read_haplogroups(a.hg_mt) if a.hg_mt else None
    attrs, cmap = assign_colors(G, hgY, hgMT)

    for i, comp in enumerate(nx.connected_components(G), 1):
        plot_static(G, comp, i, a, attrs, cmap)
        plot_html  (G, comp, i, a, attrs)

if __name__ == "__main__":
    main()

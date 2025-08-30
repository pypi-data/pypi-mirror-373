
from __future__ import annotations
import networkx as nx
import pandas as pd

def build_graph(df: pd.DataFrame,
                threshold1: float = 0.75,
                threshold2: float = 0.40,
                z1_threshold: float = 0.75,
                max_degree_fraction: float | None = None,
                drop_below_threshold2: bool = False,
                verbose: bool = False) -> nx.Graph:
    """
    Build an undirected graph from pairs (IID1, IID2, PI_HAT, Z1).

    Edge colors:
      - red:   PI_HAT > threshold1 (possible duplicates/twins/merged)
      - blue:  threshold2<=PI_HAT<=threshold1 and Z1>z1_threshold (parent–child-like)
      - green: threshold2<=PI_HAT<=threshold1 and Z1<=z1_threshold (full siblings-like)
      - gray:  PI_HAT < threshold2
    """
    G = nx.Graph()
    for _, r in df.iterrows():
        pi = float(r["PI_HAT"]); z1 = float(r.get("Z1", 0.0))
        if pi <= 0:
            continue
        if drop_below_threshold2 and pi < threshold2:
            continue
        col = ("red" if pi > threshold1 else
               "blue"  if (threshold2 <= pi <= threshold1 and z1 > z1_threshold) else
               "green" if (threshold2 <= pi <= threshold1 and z1 <= z1_threshold) else
               "gray")
        G.add_edge(str(r["IID1"]), str(r["IID2"]), weight=pi, color=col)

    if max_degree_fraction is not None:
        if not (0 < max_degree_fraction <= 1):
            raise ValueError("--max-degree-fraction must be in (0,1]")
        lim = max_degree_fraction * max(1, G.number_of_nodes())
        drop = [n for n, d in G.degree() if d > lim]
        G.remove_nodes_from(drop)
        if verbose and drop:
            print(f"[info] dropped {len(drop)} high-degree nodes")

    # remove isolates
    G.remove_nodes_from(list(nx.isolates(G)))
    if verbose:
        print(f"[info] remaining {G.number_of_nodes()} nodes / {G.number_of_edges()} edges")
    return G

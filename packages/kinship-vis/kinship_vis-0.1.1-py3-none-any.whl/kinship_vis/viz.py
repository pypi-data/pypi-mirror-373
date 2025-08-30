
from __future__ import annotations
import os
from typing import Dict, Tuple
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib import colormaps, cm
import plotly.graph_objects as go
import pandas as pd

def _palette():
    try:
        return colormaps["tab20"].colors
    except Exception:
        return cm.get_cmap("tab20").colors

def assign_colors(G: nx.Graph, hgY: pd.Series | None, hgMT: pd.Series | None):
    pal = list(_palette()); idx = 0; cmap: Dict[str, Tuple[float,float,float]] = {}
    uniq = set()
    if hgY  is not None: uniq |= set(hgY.values)
    if hgMT is not None: uniq |= set(hgMT.values)
    for h in sorted([u for u in uniq if pd.notna(u)]):
        cmap[str(h)] = pal[idx % len(pal)]; idx += 1
    cmap.update({"NA_Y":(0.4,0.4,0.4),"NA_MT":(0.7,0.7,0.7)})

    attrs = {}
    for n in G.nodes():
        y = (hgY.get(n, "NA_Y") if hgY is not None else "NA_Y")
        m = (hgMT.get(n, "NA_MT") if hgMT is not None else "NA_MT")
        attrs[n] = {"hgY": str(y), "hgMT": str(m), "colY": cmap.get(str(y), (0.4,0.4,0.4)), "colMT": cmap.get(str(m), (0.7,0.7,0.7))}
    return attrs, cmap

def ensure_parent_dir(prefix: str):
    d = os.path.dirname(prefix)
    if d:
        os.makedirs(d, exist_ok=True)

def plot_static(G, comp, cid, args, attrs, cmap):
    sg = G.subgraph(comp)
    if sg.number_of_edges() == 0:
        return
    pos = nx.spring_layout(sg, seed=42)
    fig, ax = plt.subplots(figsize=tuple(args.figsize), dpi=int(args.dpi))

    nx.draw_networkx_edges(sg, pos,
        edge_color=[d["color"] for *_, d in sg.edges(data=True)],
        width=args.edge_width, ax=ax)

    for n in sg.nodes():
        d = attrs[n]
        nx.draw_networkx_nodes(sg, pos, nodelist=[n],
            node_color=[d["colMT"]], edgecolors=[d["colY"]],
            node_size=args.node_size, linewidths=2, ax=ax)

    labels = nx.get_node_attributes(sg, "label") or {n:n for n in sg.nodes()}
    nx.draw_networkx_labels(sg, pos, labels=labels, font_size=9, ax=ax)
    ax.set_title(f"Kinship component {cid}"); ax.axis("off")

    if args.legend:
        edge_leg = {"red":f"PI_HAT>{args.threshold1}",
                    "blue":f"{args.threshold2}–{args.threshold1}, Z1>{args.z1_threshold}",
                    "green":f"{args.threshold2}–{args.threshold1}, Z1≤{args.z1_threshold}",
                    "gray":f"PI_HAT<{args.threshold2}"}
        hd=[Line2D([0],[0],color=c,lw=2,label=t) for c,t in edge_leg.items()]
        hd.append(Patch(color='none',label="MT haplogroups"))
        for h in sorted({attrs[n]["hgMT"] for n in sg.nodes()}):
            hd.append(Patch(facecolor=cmap[h],edgecolor='black',label=h))
        hd.append(Patch(color='none',label="Y haplogroups"))
        for h in sorted({attrs[n]["hgY"] for n in sg.nodes()}):
            hd.append(Line2D([0],[0],marker='o',color='w',
                             markerfacecolor='white',markeredgecolor=cmap[h],
                             markersize=10,label=h,lw=0))
        ax.legend(handles=hd,bbox_to_anchor=(1.02,1),loc="upper left",
                  fontsize=8,borderaxespad=0)
    fig.tight_layout()
    ensure_parent_dir(args.output)
    fout = f"{args.output}_component_{cid}.{args.format}"
    fig.savefig(fout, bbox_inches="tight"); plt.close(fig)

def plot_html(G, comp, cid, args, attrs):
    sg = G.subgraph(comp)
    if sg.number_of_edges() == 0:
        return
    pos = nx.spring_layout(sg, seed=42)

    edge_desc = {"red":f"PI_HAT>{args.threshold1}",
                 "blue":f"{args.threshold2}–{args.threshold1}, Z1>{args.z1_threshold}",
                 "green":f"{args.threshold2}–{args.threshold1}, Z1≤{args.z1_threshold}",
                 "gray":f"PI_HAT<{args.threshold2}"}
    edge_traces = []
    for col in ["red","blue","green","gray"]:
        xe, ye = [], []
        for u, v, d in sg.edges(data=True):
            if d["color"] != col:
                continue
            xe += [pos[u][0], pos[v][0], None]
            ye += [pos[u][1], pos[v][1], None]
        if xe:
            edge_traces.append(go.Scatter(
                x=xe, y=ye, mode="lines",
                line=dict(width=2, color=col),
                hoverinfo="none",
                name=edge_desc[col],
                showlegend=bool(args.legend)))

    labels = nx.get_node_attributes(sg, "label")
    txt   = [labels.get(n, n) for n in sg.nodes()]
    hover = [f"{n}<br>Y:{attrs[n]['hgY']} MT:{attrs[n]['hgMT']}" for n in sg.nodes()]
    fill  = [attrs[n]["colMT"] for n in sg.nodes()]
    border= [attrs[n]["colY"] for n in sg.nodes()]
    x = [pos[n][0] for n in sg.nodes()]
    y = [pos[n][1] for n in sg.nodes()]

    node = go.Scatter(x=x, y=y, mode="markers+text", text=txt,
        textposition="bottom center", hovertext=hover, hoverinfo="text",
        marker=dict(size=int(args.node_size_html), color=fill, line=dict(width=2, color=border)),
        showlegend=False)

    legend_traces = []
    if args.legend:
        mt_colors: Dict[str, Tuple[float, float, float]] = {}
        y_colors: Dict[str, Tuple[float, float, float]] = {}
        for n in sg.nodes():
            mt_colors[attrs[n]["hgMT"]] = attrs[n]["colMT"]
            y_colors[attrs[n]["hgY"]] = attrs[n]["colY"]

        legend_traces.append(go.Scatter(x=[None], y=[None], mode="markers",
                                        marker=dict(size=0, color="rgba(0,0,0,0)"),
                                        name="MT haplogroups", hoverinfo="none"))
        for h in sorted(mt_colors):
            legend_traces.append(go.Scatter(x=[None], y=[None], mode="markers",
                                            marker=dict(size=int(args.node_size_html),
                                                        color=mt_colors[h],
                                                        line=dict(width=1, color="black")),
                                            name=h, hoverinfo="none"))
        legend_traces.append(go.Scatter(x=[None], y=[None], mode="markers",
                                        marker=dict(size=0, color="rgba(0,0,0,0)"),
                                        name="Y haplogroups", hoverinfo="none"))
        for h in sorted(y_colors):
            legend_traces.append(go.Scatter(x=[None], y=[None], mode="markers",
                                            marker=dict(size=int(args.node_size_html),
                                                        color="white",
                                                        line=dict(width=2, color=y_colors[h])),
                                            name=h, hoverinfo="none"))

    fig = go.Figure(edge_traces + legend_traces + [node],
        layout=go.Layout(title=f"Kinship component {cid}",
                         paper_bgcolor="white", plot_bgcolor="white",
                         xaxis=dict(visible=False), yaxis=dict(visible=False),
                         showlegend=bool(args.legend)))
    ensure_parent_dir(args.output)
    fout = f"{args.output}_component_{cid}.html"
    fig.write_html(fout)

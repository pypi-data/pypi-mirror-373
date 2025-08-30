
import io, pandas as pd
import pytest
from kinship_vis.graph import build_graph
from kinship_vis.io import read_pairs_table

def test_build_graph_smoke(tmp_path):
    genome = io.StringIO("IID1 IID2 PI_HAT Z1\nA B 0.9 0.95\nA C 0.45 0.9\nD E 0.1 0.0\n")
    df = pd.read_csv(genome, sep=r"\s+")
    G = build_graph(df, verbose=True)
    assert G.number_of_nodes() >= 3
    comps = list(map(len, map(list, __import__("networkx").connected_components(G))))
    assert max(comps) >= 3

def test_read_king_kin0(tmp_path):
    kin0 = io.StringIO("ID1 ID2 Kinship\nA B 0.5\nC D 0.125\n")
    kin_path = tmp_path / "x.kin0"
    kin_path.write_text(kin0.getvalue(), encoding="utf-8")
    df = read_pairs_table(str(kin_path))
    assert {"IID1","IID2","PI_HAT","Z1"}.issubset(df.columns)
    assert df["PI_HAT"].iloc[0] == 1.0


def test_read_pairs_missing_file():
    with pytest.raises(FileNotFoundError):
        read_pairs_table("/no/such/file")


def test_read_pairs_bad_format(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("a b c\n1 2 3\n", encoding="utf-8")
    with pytest.raises(ValueError):
        read_pairs_table(str(bad))

from kinship_vis.io import read_haplogroups, read_samplesheet


def test_read_haplogroups_whitespace(tmp_path):
    txt = " A   H1 \nB\tH2\nC   H3  extra\n"
    path = tmp_path / "hg.txt"
    path.write_text(txt, encoding="utf-8")
    s = read_haplogroups(str(path))
    assert s.to_dict() == {"A": "H1", "B": "H2", "C": "H3"}


def test_read_samplesheet_whitespace(tmp_path):
    txt = """sample_id cohort note\nA   grp1   foo  \nB\tgrp2\tbar \n"""
    path = tmp_path / "samples.txt"
    path.write_text(txt, encoding="utf-8")
    df = read_samplesheet(str(path))
    assert list(df.columns) == ["sample_id", "cohort", "note"]
    assert df.loc[0, "note"] == "foo"
    assert df.loc[1, "note"] == "bar"


def test_read_samplesheet_csv(tmp_path):
    txt = """sample_id,cohort,note\nA,grp1,foo\nB,grp2,bar\n"""
    path = tmp_path / "samples.csv"
    path.write_text(txt, encoding="utf-8")
    df = read_samplesheet(str(path))
    assert list(df.columns) == ["sample_id", "cohort", "note"]
    assert df.loc[0, "cohort"] == "grp1"
    assert df.loc[1, "note"] == "bar"

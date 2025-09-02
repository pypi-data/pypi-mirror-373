import types

from ivybloom_cli.commands import run as run_cmd


def test_normalize_param_keys_basic():
    data = {"ligand-file": {"inner-key": 1}, "protein_file": 2}
    out = run_cmd._normalize_param_keys(data)
    assert set(out.keys()) == {"ligand_file", "protein_file"}
    assert set(out["ligand_file"].keys()) == {"inner_key"}


def test_parse_feature_directives_values_and_bools():
    needs = ("primary=pdb", "scores",)
    wants = ("summary=true", "thumbnails=false")
    features = ("use-fast-mode=true", "max_steps=1000",)
    d = run_cmd._parse_feature_directives(needs, wants, features)
    assert d["need"]["primary"] == "pdb"
    assert d["need"]["scores"] is True
    assert d["want"]["summary"] is True
    assert d["want"]["thumbnails"] is False
    assert d["flags"]["use_fast_mode"] is True
    assert d["flags"]["max_steps"] == 1000


def test_validation_ignores_reserved_features_key():
    schema = {"parameters": {"properties": {"a": {"type": "string"}}, "required": ["a"]}}
    params = {"a": "x", "__features__": {"want": {"scores": True}}}
    errs = run_cmd._validate_parameters(params, schema)
    assert errs == []


def test_uniprot_accession_detection():
    assert run_cmd._looks_like_uniprot_accession("P69905")
    assert run_cmd._looks_like_uniprot_accession("Q9XYZ1")
    assert not run_cmd._looks_like_uniprot_accession("INVALID123")


def test_preprocess_esmfold_maps_protein_and_uniprot(monkeypatch):
    # Mock resolver
    monkeypatch.setattr(run_cmd, "_resolve_uniprot_sequence", lambda acc: "MPEPTIDE" if acc == "P69905" else "")
    schema = {"parameters": {"properties": {"protein_sequence": {"type": "string"}}}}
    params = {"uniprot": "P69905"}
    out = run_cmd._preprocess_tool_parameters("esmfold", params, schema)
    assert out.get("protein_sequence") == "MPEPTIDE"
    assert "uniprot" not in out

    params2 = {"protein": "ACDEFGHIKLMNPQRSTVWY"}
    out2 = run_cmd._preprocess_tool_parameters("esmfold", params2, schema)
    assert out2.get("protein_sequence") == "ACDEFGHIKLMNPQRSTVWY"
    assert "protein" not in out2



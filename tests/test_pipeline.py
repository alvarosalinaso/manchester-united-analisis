"""Tests de reporting y de punta a punta (el pipeline escribe solo en tmp)."""

import json
import shutil

import pytest

from manutd_analysis import reporting
from manutd_analysis.config import ProjectPaths
from manutd_analysis.pipeline import compute, main, run


def test_replace_marker_no_interpreta_backreferences():
    out = reporting.replace_marker("a <!-- FIND:x -->old<!-- /FIND:x --> b", "x", r"new \1")
    assert out == r"a <!-- FIND:x -->new \1<!-- /FIND:x --> b"


def test_replace_marker_inexistente():
    with pytest.raises(reporting.MarkerNotFoundError):
        reporting.replace_marker("sin marcadores", "x", "y")


def test_sync_document(tmp_path):
    doc = tmp_path / "README.md"
    doc.write_text("<!-- FIND:brecha -->0<!-- /FIND:brecha -->", encoding="utf-8")
    assert reporting.sync_document(doc, {"brecha": "23.1", "otro": "x"})
    assert "23.1" in doc.read_text(encoding="utf-8")
    assert not reporting.sync_document(doc, {"brecha": "23.1"})
    assert not reporting.sync_document(tmp_path / "no.md", {"brecha": "1"})


def test_pipeline_end_to_end(tmp_path, repo_paths):
    shutil.copy(repo_paths.readme, tmp_path / "README.md")
    shutil.copy(repo_paths.dashboard_html, tmp_path / "dashboard.html")
    out = ProjectPaths(root=tmp_path)

    result = run(out=out, pl_csv=repo_paths.pl_tables_csv, passing_csv=repo_paths.passing_csv)

    assert all(p.exists() for p in result.outputs)
    for json_file in out.export_dir.glob("*.json"):
        assert "NaN" not in json_file.read_text(encoding="utf-8"), json_file.name
    findings = json.loads((out.export_dir / "key_findings.json").read_text(encoding="utf-8"))
    assert findings["brecha_media"] == result.findings["brecha_media"]
    assert out.season_kpis_csv.exists()
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert f"<!-- FIND:brecha -->{findings['brecha_media']:.1f}<!-- /FIND:brecha -->" in readme


def test_readme_y_dashboard_publicados_estan_sincronizados(repo_paths):
    """Lo publicado en README y dashboard debe coincidir con lo que calcula el pipeline."""
    f = compute(repo_paths.pl_tables_csv, repo_paths.passing_csv).findings
    readme = repo_paths.readme.read_text(encoding="utf-8")
    dashboard = repo_paths.dashboard_html.read_text(encoding="utf-8")
    assert f"<!-- FIND:brecha -->{f['brecha_media']:.1f}<!-- /FIND:brecha -->" in readme
    assert f"<!-- FIND:brecha -->{f['brecha_media']:.1f} pts<!-- /FIND:brecha -->" in dashboard


def test_cli_devuelve_2_si_faltan_datos(monkeypatch, tmp_path):
    monkeypatch.setenv("MANUTD_ROOT", str(tmp_path))
    assert main(["--no-sync", "--no-figures"]) == 2

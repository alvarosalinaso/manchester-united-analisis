"""Tests para src/findings.py, hallazgos clave sincronizados."""

from pathlib import Path

from src.findings import compute_findings, sync_findings

ROOT = Path(__file__).resolve().parent.parent


def test_compute_findings_valores_reales():
    f = compute_findings()
    assert f["n_temporadas"] == 11
    assert f["brecha_media"] == 23.1
    assert f["peor_dt"]["nombre"] == "David Moyes"
    assert abs(f["peor_dt"]["ppg"] - 1.68) < 0.01
    assert f["mejor_dt"]["nombre"] == "José Mourinho"
    assert abs(f["mejor_dt"]["ppg"] - 1.97) < 0.01
    assert f["costo_inestabilidad"] > 0


def test_sync_findings_actualiza_readme_y_dashboard(tmp_path):
    readme = tmp_path / "README.md"
    dashboard = tmp_path / "dashboard.html"
    readme.write_text(
        "<!-- FIND:table -->OLD<!-- /FIND:table -->\n"
        "gap <!-- FIND:brecha -->0<!-- /FIND:brecha --> pts",
        encoding="utf-8",
    )
    dashboard.write_text(
        '<div class="kpi-value"><!-- FIND:brecha -->0<!-- /FIND:brecha --></div>'
        '<div class="kpi-value"><!-- FIND:costo -->0<!-- /FIND:costo --></div>',
        encoding="utf-8",
    )

    f = sync_findings(tmp_path)

    readme_text = readme.read_text(encoding="utf-8")
    dashboard_text = dashboard.read_text(encoding="utf-8")
    assert "23.1" in readme_text
    assert "David Moyes" in readme_text
    assert f"<!-- FIND:brecha -->{f['brecha_media']:.1f}<!-- /FIND:brecha -->" in readme_text
    assert f"<!-- FIND:brecha -->{f['brecha_media']:.1f} pts<!-- /FIND:brecha -->" in dashboard_text
    assert f"<!-- FIND:costo -->~{f['costo_inestabilidad']:.1f} pts<!-- /FIND:costo -->" in (
        dashboard_text
    )
    assert (tmp_path / "data" / "export" / "key_findings.json").exists()


def test_readme_y_dashboard_usan_misma_brecha():
    f = compute_findings()
    brecha = f"{f['brecha_media']:.1f}"
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    dashboard_text = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    assert f"<!-- FIND:brecha -->{brecha}<!-- /FIND:brecha -->" in readme_text
    assert f"<!-- FIND:brecha -->{brecha} pts<!-- /FIND:brecha -->" in dashboard_text

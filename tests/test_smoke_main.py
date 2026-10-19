"""Test de humo: main.py debe correr de punta a punta sin errores."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")


def test_main_smoke(monkeypatch):
    """Ejecuta el pipeline completo de main.main() sin excepciones."""
    root = Path(__file__).resolve().parent.parent
    monkeypatch.chdir(root)

    import main

    main.main()

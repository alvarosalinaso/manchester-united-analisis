"""Atajo de compatibilidad: equivale a ``python -m manutd_analysis``."""

import sys

from manutd_analysis.pipeline import main

if __name__ == "__main__":
    sys.exit(main())

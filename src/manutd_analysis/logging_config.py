"""Configuración de logging del proyecto (un único punto de entrada)."""

from __future__ import annotations

import logging
import os

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%H:%M:%S"


def setup_logging(level: str | int | None = None) -> None:
    """Configura el logger raíz una sola vez.

    Parameters
    ----------
    level : str | int | None
        Nivel de logging. Si es ``None`` se usa la variable de entorno
        ``MANUTD_LOG_LEVEL`` o ``INFO`` por defecto.
    """
    resolved = level if level is not None else os.getenv("MANUTD_LOG_LEVEL", "INFO")
    logging.basicConfig(level=resolved, format=LOG_FORMAT, datefmt=DATE_FORMAT, force=True)
    # Librerías ruidosas: solo advertencias.
    for noisy in ("matplotlib", "PIL", "fontTools"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

"""Utilidades para serialización JSON con tipos numpy."""


def json_default(obj):
    """Convierte tipos numpy (bool/int/float) a tipos nativos de Python."""
    if hasattr(obj, "item"):
        return obj.item()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

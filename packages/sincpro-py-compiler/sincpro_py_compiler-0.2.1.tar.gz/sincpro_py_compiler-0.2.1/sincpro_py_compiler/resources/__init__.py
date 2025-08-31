"""
Módulo de recursos para SincPro Python Compiler.

Este módulo contiene archivos de configuración, templates y recursos
que son incluidos en el build del paquete.
"""

from pathlib import Path

# Directorio raíz de recursos
RESOURCES_DIR = Path(__file__).parent.absolute()

# Subdirectorios de recursos
TEMPLATES_DIR = RESOURCES_DIR / "templates"
EXCLUDE_PATTERNS_DIR = RESOURCES_DIR / "exclude_patterns"

__all__ = [
    "RESOURCES_DIR",
    "TEMPLATES_DIR",
    "EXCLUDE_PATTERNS_DIR",
]

"""
Gestión de recursos para templates y patrones de exclusión.
"""

from pathlib import Path
from typing import Dict, List

from . import EXCLUDE_PATTERNS_DIR, RESOURCES_DIR


class ResourceManager:
    """Gestiona los recursos del paquete."""

    @staticmethod
    def get_exclude_patterns(template_name: str) -> List[str]:
        """
        Obtiene patrones de exclusión desde archivo de template.

        Args:
            template_name: Nombre del template (ej: 'basic', 'django', 'odoo')

        Returns:
            Lista de patrones de exclusión
        """
        template_file = EXCLUDE_PATTERNS_DIR / f"{template_name}.txt"

        if not template_file.exists():
            raise FileNotFoundError(f"Template '{template_name}' no encontrado")

        patterns = []
        with open(template_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Ignorar líneas vacías y comentarios
                if line and not line.startswith("#"):
                    patterns.append(line)

        return patterns

    @staticmethod
    def list_available_templates() -> Dict[str, str]:
        """
        Lista templates disponibles con sus descripciones.

        Returns:
            Diccionario con nombre del template y descripción
        """
        templates = {}

        for template_file in EXCLUDE_PATTERNS_DIR.glob("*.txt"):
            template_name = template_file.stem

            # Leer primera línea que contiene la descripción
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("#"):
                        description = first_line[1:].strip()
                    else:
                        description = f"Template de exclusión para {template_name}"
                    templates[template_name] = description
            except Exception:
                templates[template_name] = f"Template de exclusión para {template_name}"

        return templates

    @staticmethod
    def resource_exists(resource_path: str) -> bool:
        """
        Verifica si un recurso existe.

        Args:
            resource_path: Ruta relativa del recurso desde RESOURCES_DIR

        Returns:
            True si el recurso existe
        """
        return (RESOURCES_DIR / resource_path).exists()

    @staticmethod
    def get_resource_path(resource_path: str) -> Path:
        """
        Obtiene la ruta absoluta de un recurso.

        Args:
            resource_path: Ruta relativa del recurso desde RESOURCES_DIR

        Returns:
            Ruta absoluta del recurso
        """
        return RESOURCES_DIR / resource_path


def load_exclude_template(template_name: str) -> List[str]:
    """
    Función de conveniencia para cargar un template de exclusión.

    Args:
        template_name: Nombre del template

    Returns:
        Lista de patrones de exclusión
    """
    return ResourceManager.get_exclude_patterns(template_name)


def list_exclude_templates() -> Dict[str, str]:
    """
    Función de conveniencia para listar templates disponibles.

    Returns:
        Diccionario con templates y descripciones
    """
    return ResourceManager.list_available_templates()

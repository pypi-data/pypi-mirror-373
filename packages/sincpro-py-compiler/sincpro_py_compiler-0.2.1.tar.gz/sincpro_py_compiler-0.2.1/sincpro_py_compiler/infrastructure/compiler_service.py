"""
Implementación concreta del servicio de compilación
"""

import logging
import os
import py_compile
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CompilerService:
    """Implementación concreta del servicio de compilación"""

    def __init__(self):
        # Templates de exclusión y copia fiel
        self.templates: Dict[str, Dict[str, List[str]]] = {
            "basic": {
                "exclude": [
                    "__pycache__/",
                    "*.pyc",
                    ".git/",
                    ".venv/",
                    "venv/",
                    "env/",
                    ".env/",
                    "*.log",
                    ".DS_Store",
                ],
                "copy_faithful": [],
            },
            "django": {
                "exclude": [
                    "__pycache__/",
                    "*.pyc",
                    ".git/",
                    ".venv/",
                    "venv/",
                    "env/",
                    ".env/",
                    "*.log",
                    ".DS_Store",
                    "migrations/",
                    "static/",
                    "media/",
                    "db.sqlite3",
                ],
                "copy_faithful": [],
            },
            "odoo": {
                "exclude": [
                    "__pycache__/",
                    "*.pyc",
                    ".git/",
                    ".venv/",
                    "venv/",
                    "env/",
                    ".env/",
                    "*.log",
                    ".DS_Store",
                ],
                "copy_faithful": [
                    "__manifest__.py",
                    "__openerp__.py",
                    "static/",
                    "data/",
                    "demo/",
                    "security/",
                ],
            },
        }

    def should_exclude(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Determina si un archivo debe ser excluido"""
        file_str = str(file_path)
        for pattern in exclude_patterns:
            if pattern.endswith("/"):
                # Es un directorio
                if f"/{pattern}" in file_str or file_str.startswith(pattern):
                    return True
            elif "*" in pattern:
                # Es un patrón con wildcard
                if pattern.startswith("*."):
                    extension = pattern[1:]
                    if file_str.endswith(extension):
                        return True
            else:
                # Es un archivo específico
                if file_path.name == pattern or file_str.endswith(f"/{pattern}"):
                    return True
        return False

    def should_copy_faithful(self, file_path: Path, copy_patterns: List[str]) -> bool:
        """Determina si un archivo debe copiarse fielmente"""
        file_str = str(file_path)
        for pattern in copy_patterns:
            if pattern.endswith("/"):
                # Es un directorio
                if f"/{pattern}" in file_str or file_str.startswith(pattern):
                    return True
            else:
                # Es un archivo específico
                if file_path.name == pattern or file_str.endswith(f"/{pattern}"):
                    return True
        return False

    def get_exclude_patterns(
        self, template: Optional[str] = None, custom_file: Optional[str] = None
    ) -> List[str]:
        """Obtiene patrones de exclusión"""
        patterns = []
        if template and template in self.templates:
            patterns.extend(self.templates[template]["exclude"])
        if custom_file and os.path.exists(custom_file):
            with open(custom_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        return patterns

    def get_copy_faithful_patterns(self, template: Optional[str] = None) -> List[str]:
        """Obtiene patrones de copia fiel"""
        if template and template in self.templates:
            return self.templates[template]["copy_faithful"]
        return []

    def compile_python_file(self, source_file: Path, output_file: Path) -> bool:
        """Compila un archivo Python"""
        try:
            py_compile.compile(str(source_file), str(output_file), doraise=True)
            logger.debug(f"Compilado: {source_file.name} -> {output_file.name}")
            return True
        except Exception as e:
            logger.error(f"Error compilando {source_file}: {e}")
            return False

    def list_available_templates(self) -> List[str]:
        """Lista templates disponibles"""
        return list(self.templates.keys())

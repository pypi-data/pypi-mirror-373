"""
Dominio - Interfaces y contratos para el compilador de Python
"""

from pathlib import Path
from typing import List, Optional, Protocol


class CompilerServiceProtocol(Protocol):
    """Protocolo que define el contrato para servicios de compilación"""

    def should_exclude(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Determina si un archivo debe ser excluido"""
        ...

    def get_exclude_patterns(
        self, template: Optional[str] = None, custom_file: Optional[str] = None
    ) -> List[str]:
        """Obtiene patrones de exclusión"""
        ...

    def compile_python_file(self, source_file: Path, output_file: Path) -> bool:
        """Compila un archivo Python"""
        ...

    def list_available_templates(self) -> List[str]:
        """Lista templates disponibles"""
        ...


class FileManagerProtocol(Protocol):
    """Protocolo para manejo de archivos y directorios"""

    def copy_file(self, source: Path, destination: Path) -> bool:
        """Copia un archivo preservando metadatos"""
        ...

    def create_directory(self, directory: Path) -> bool:
        """Crea un directorio si no existe"""
        ...

    def walk_directory(self, directory: Path) -> List[Path]:
        """Recorre un directorio y retorna lista de archivos"""
        ...


class ProjectCompilerProtocol(Protocol):
    """Protocolo principal para compilación de proyectos"""

    def compile_project(
        self,
        source_dir: str,
        output_dir: str,
        template: str = "basic",
        exclude_file: Optional[str] = None,
        remove_py: bool = False,
    ) -> bool:
        """Compila un proyecto completo"""
        ...

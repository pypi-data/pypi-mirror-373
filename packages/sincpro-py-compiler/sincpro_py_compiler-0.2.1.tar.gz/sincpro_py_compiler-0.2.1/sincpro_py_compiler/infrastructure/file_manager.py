"""
Implementación concreta para manejo de archivos
"""

import logging
import os
import shutil
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class FileManager:
    """Implementación concreta para operaciones de archivos"""

    def copy_file(self, source: Path, destination: Path) -> bool:
        """Copia un archivo preservando metadatos"""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(destination))
            logger.debug(f"Copiado: {source.name}")
            return True
        except Exception as e:
            logger.error(f"Error copiando {source}: {e}")
            return False

    def create_directory(self, directory: Path) -> bool:
        """Crea un directorio si no existe"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creando directorio {directory}: {e}")
            return False

    def walk_directory(self, directory: Path) -> List[Path]:
        """Recorre un directorio y retorna lista de archivos"""
        files = []
        try:
            for root, dirs, file_names in os.walk(directory):
                for file_name in file_names:
                    files.append(Path(root) / file_name)
        except Exception as e:
            logger.error(f"Error recorriendo directorio {directory}: {e}")
        return files

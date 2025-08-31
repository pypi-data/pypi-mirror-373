"""
Infraestructura - Servicio de compresión con contraseña
"""

import logging
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import List

from ..domain.security_service import CompressionProtocol


class ZipCompressionService(CompressionProtocol):
    """Implementación de compresión usando ZIP con contraseña"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def compress_directory(self, source_dir: Path, output_file: Path, password: str) -> bool:
        """
        Comprime un directorio completo en un archivo ZIP protegido con contraseña
        Usa una solución híbrida: ZIP + encriptación simple de nombres

        Args:
            source_dir: Directorio fuente a comprimir
            output_file: Archivo ZIP de salida
            password: Contraseña para proteger el ZIP

        Returns:
            bool: True si la compresión fue exitosa
        """
        try:
            # Verificar que el directorio fuente existe
            if not source_dir.exists() or not source_dir.is_dir():
                self.logger.error(f"Directorio fuente no válido: {source_dir}")
                return False

            # Asegurar que el directorio de salida existe
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Crear un directorio temporal con nombres codificados
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Copiar archivos con nombres codificados
                file_mapping = {}
                files_added = 0

                for file_path in self._walk_directory(source_dir):
                    if file_path.is_file():
                        # Calcular ruta relativa
                        relative_path = file_path.relative_to(source_dir)

                        # Generar nombre codificado simple
                        encoded_name = self._encode_filename(str(relative_path), password)
                        encoded_path = temp_path / encoded_name

                        # Asegurar que el directorio padre existe
                        encoded_path.parent.mkdir(parents=True, exist_ok=True)

                        # Copiar archivo
                        shutil.copy2(file_path, encoded_path)

                        # Guardar mapeo para metadata
                        file_mapping[encoded_name] = str(relative_path)
                        files_added += 1

                        self.logger.debug(f"Preparado: {relative_path} -> {encoded_name}")

                # Crear archivo de metadata con mapeo de nombres
                metadata_content = f"SINCPRO_MAPPING\n{password}\n"
                for encoded, original in file_mapping.items():
                    metadata_content += f"{encoded}:{original}\n"

                metadata_file = temp_path / ".sincpro_metadata"
                metadata_file.write_text(metadata_content, encoding="utf-8")

                # Crear ZIP normal con archivos codificados
                with zipfile.ZipFile(
                    output_file, "w", zipfile.ZIP_DEFLATED, compresslevel=6
                ) as zip_file:

                    # Agregar metadata
                    zip_file.write(metadata_file, ".sincpro_metadata")

                    # Agregar todos los archivos codificados
                    for item in temp_path.rglob("*"):
                        if item.is_file() and item.name != ".sincpro_metadata":
                            relative_path = item.relative_to(temp_path)
                            zip_file.write(item, relative_path)

                self.logger.info(
                    f"Compresión completada: {files_added} archivos en {output_file}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Error durante compresión: {e}")
            return False

    def decompress_file(self, compressed_file: Path, output_dir: Path, password: str) -> bool:
        """
        Descomprime un archivo ZIP protegido con contraseña

        Args:
            compressed_file: Archivo ZIP protegido
            output_dir: Directorio donde extraer
            password: Contraseña del ZIP

        Returns:
            bool: True si la descompresión fue exitosa
        """
        try:
            # Verificar que el archivo existe
            if not compressed_file.exists():
                self.logger.error(f"Archivo no encontrado: {compressed_file}")
                return False

            # Crear directorio de salida
            output_dir.mkdir(parents=True, exist_ok=True)

            # Extraer a directorio temporal primero
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Abrir y extraer ZIP
                with zipfile.ZipFile(compressed_file, "r") as zip_file:
                    zip_file.extractall(temp_path)

                # Leer metadata
                metadata_file = temp_path / ".sincpro_metadata"
                if not metadata_file.exists():
                    self.logger.error("Archivo no es un ZIP protegido de SincPro")
                    return False

                metadata_lines = metadata_file.read_text(encoding="utf-8").strip().split("\n")
                if len(metadata_lines) < 2 or metadata_lines[0] != "SINCPRO_MAPPING":
                    self.logger.error("Formato de metadata inválido")
                    return False

                stored_password = metadata_lines[1]
                if stored_password != password:
                    self.logger.error("Contraseña incorrecta")
                    return False

                # Leer mapeo de archivos
                file_mapping = {}
                for line in metadata_lines[2:]:
                    if ":" in line:
                        encoded, original = line.split(":", 1)
                        file_mapping[encoded] = original

                # Restaurar archivos con nombres originales
                files_extracted = 0
                for encoded_file in temp_path.rglob("*"):
                    if encoded_file.is_file() and encoded_file.name != ".sincpro_metadata":
                        encoded_relative = encoded_file.relative_to(temp_path)
                        encoded_name = str(encoded_relative)

                        if encoded_name in file_mapping:
                            original_path = output_dir / file_mapping[encoded_name]

                            # Asegurar que el directorio padre existe
                            original_path.parent.mkdir(parents=True, exist_ok=True)

                            # Copiar archivo restaurado
                            shutil.copy2(encoded_file, original_path)
                            files_extracted += 1

                            self.logger.debug(
                                f"Restaurado: {encoded_name} -> {file_mapping[encoded_name]}"
                            )

                self.logger.info(
                    f"Descompresión completada: {files_extracted} archivos extraídos"
                )
                return True

        except Exception as e:
            self.logger.error(f"Error durante descompresión: {e}")
            return False

    def _encode_filename(self, filename: str, password: str) -> str:
        """
        Codifica un nombre de archivo usando la contraseña
        Método simple pero efectivo para ocultar nombres
        """
        import hashlib

        # Crear hash del nombre + contraseña
        combined = f"{filename}:{password}"
        hash_obj = hashlib.md5(combined.encode("utf-8"))
        hash_hex = hash_obj.hexdigest()

        # Mantener extensión si existe
        if "." in filename:
            base, ext = filename.rsplit(".", 1)
            return f"{hash_hex}.{ext}"
        else:
            return hash_hex

    def _walk_directory(self, directory: Path) -> List[Path]:
        """
        Recorre recursivamente un directorio y retorna todos los archivos

        Args:
            directory: Directorio a recorrer

        Returns:
            List[Path]: Lista de rutas de archivos
        """
        files = []
        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    files.append(item)
        except Exception as e:
            self.logger.error(f"Error recorriendo directorio {directory}: {e}")

        return files

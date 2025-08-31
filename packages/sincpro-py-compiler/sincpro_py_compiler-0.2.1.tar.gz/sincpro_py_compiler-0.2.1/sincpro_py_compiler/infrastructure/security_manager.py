"""
Infraestructura - Manager de seguridad que orquesta compresión y encriptación
"""

import logging
from pathlib import Path
from typing import Optional

from ..domain.security_service import SecurityServiceProtocol
from .compression_service import ZipCompressionService
from .encryption_service import SimpleEncryptionService


class SecurityManager(SecurityServiceProtocol):
    """
    Manager principal que orquesta los servicios de seguridad
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compression_service = ZipCompressionService()

        # Inicializar servicio de encriptación con manejo de errores
        try:
            self.encryption_service = SimpleEncryptionService()
            self.encryption_available = True
        except ImportError as e:
            self.logger.warning(f"Encriptación no disponible: {e}")
            self.encryption_service = None
            self.encryption_available = False

    def protect_compiled_code(
        self, compiled_dir: Path, output_file: Path, password: str, method: str = "compress"
    ) -> bool:
        """
        Protege código compilado usando el método especificado

        Args:
            compiled_dir: Directorio con código compilado
            output_file: Archivo de salida protegido
            password: Contraseña/licencia para protección
            method: 'compress' o 'encrypt'

        Returns:
            bool: True si la protección fue exitosa
        """
        if not compiled_dir.exists() or not compiled_dir.is_dir():
            self.logger.error(f"Directorio fuente no válido: {compiled_dir}")
            return False

        if not password or len(password.strip()) == 0:
            self.logger.error("Contraseña requerida para protección")
            return False

        self.logger.info(f"Protegiendo código con método: {method}")

        if method == "compress":
            return self._protect_with_compression(compiled_dir, output_file, password)
        elif method == "encrypt":
            return self._protect_with_encryption(compiled_dir, output_file, password)
        else:
            self.logger.error(f"Método de protección no válido: {method}")
            return False

    def unprotect_code(self, protected_file: Path, output_dir: Path, password: str) -> bool:
        """
        Desprotege código detectando automáticamente el método usado

        Args:
            protected_file: Archivo protegido
            output_dir: Directorio de salida
            password: Contraseña/licencia para desprotección

        Returns:
            bool: True si la desprotección fue exitosa
        """
        if not protected_file.exists():
            self.logger.error(f"Archivo protegido no encontrado: {protected_file}")
            return False

        if not password or len(password.strip()) == 0:
            self.logger.error("Contraseña requerida para desprotección")
            return False

        # Detectar método de protección
        method = self.detect_protection_method(protected_file)
        if not method:
            self.logger.error("No se pudo detectar el método de protección")
            return False

        self.logger.info(f"Desprotegiendo código con método: {method}")

        if method == "compress":
            return self.compression_service.decompress_file(
                protected_file, output_dir, password
            )
        elif method == "encrypt":
            if not self.encryption_available:
                self.logger.error("Servicio de encriptación no disponible")
                return False
            return self.encryption_service.decrypt_file(  # type: ignore
                protected_file, output_dir, password
            )
        else:
            self.logger.error(f"Método de desprotección no válido: {method}")
            return False

    def detect_protection_method(self, protected_file: Path) -> Optional[str]:
        """
        Detecta el método de protección usado en un archivo

        Args:
            protected_file: Archivo protegido a analizar

        Returns:
            Optional[str]: 'compress', 'encrypt', o None si no se puede detectar
        """
        try:
            # Verificar si es un archivo ZIP
            import zipfile

            if zipfile.is_zipfile(protected_file):
                self.logger.debug("Archivo detectado como ZIP comprimido")
                return "compress"

            # Verificar si es un archivo encriptado por nuestro sistema
            with open(protected_file, "rb") as f:
                # Intentar leer metadata
                try:
                    metadata_size = int.from_bytes(f.read(4), "big")
                    if 4 <= metadata_size <= 1024:  # Tamaño razonable para metadata
                        metadata_json = f.read(metadata_size)
                        separator = f.read(len(b"---SINCPRO_SEPARATOR---"))

                        if separator == b"---SINCPRO_SEPARATOR---":
                            import json

                            metadata = json.loads(metadata_json.decode("utf-8"))
                            if metadata.get("method") == "encrypt":
                                self.logger.debug("Archivo detectado como encriptado")
                                return "encrypt"
                except Exception:
                    pass

            self.logger.warning("No se pudo detectar el método de protección")
            return None

        except Exception as e:
            self.logger.error(f"Error detectando método de protección: {e}")
            return None

    def _protect_with_compression(
        self, compiled_dir: Path, output_file: Path, password: str
    ) -> bool:
        """Protege usando compresión ZIP"""
        try:
            # Asegurar extensión .zip
            if not output_file.suffix.lower() == ".zip":
                output_file = output_file.with_suffix(".zip")

            return self.compression_service.compress_directory(
                compiled_dir, output_file, password
            )
        except Exception as e:
            self.logger.error(f"Error en protección por compresión: {e}")
            return False

    def _protect_with_encryption(
        self, compiled_dir: Path, output_file: Path, password: str
    ) -> bool:
        """Protege usando encriptación"""
        if not self.encryption_available:
            self.logger.error(
                "Servicio de encriptación no disponible. "
                "Instale cryptography: pip install cryptography"
            )
            return False

        try:
            # Asegurar extensión .enc
            if not output_file.suffix.lower() == ".enc":
                output_file = output_file.with_suffix(".enc")

            return self.encryption_service.encrypt_directory(  # type: ignore
                compiled_dir, output_file, password
            )
        except Exception as e:
            self.logger.error(f"Error en protección por encriptación: {e}")
            return False

    def is_encryption_available(self) -> bool:
        """Verifica si el servicio de encriptación está disponible"""
        return self.encryption_available

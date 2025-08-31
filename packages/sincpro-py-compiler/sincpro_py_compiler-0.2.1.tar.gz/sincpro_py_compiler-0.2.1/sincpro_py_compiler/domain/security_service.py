"""
Dominio - Interfaces y contratos para servicios de seguridad
"""

from pathlib import Path
from typing import Optional, Protocol


class CompressionProtocol(Protocol):
    """Protocolo para servicios de compresión"""

    def compress_directory(self, source_dir: Path, output_file: Path, password: str) -> bool:
        """Comprime un directorio con contraseña"""
        ...

    def decompress_file(self, compressed_file: Path, output_dir: Path, password: str) -> bool:
        """Descomprime un archivo protegido"""
        ...


class EncryptionProtocol(Protocol):
    """Protocolo para servicios de encriptación"""

    def encrypt_directory(self, source_dir: Path, output_file: Path, password: str) -> bool:
        """Encripta un directorio completo"""
        ...

    def decrypt_file(self, encrypted_file: Path, output_dir: Path, password: str) -> bool:
        """Desencripta un archivo protegido"""
        ...


class SecurityServiceProtocol(Protocol):
    """Protocolo principal para servicios de seguridad"""

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
        """
        ...

    def unprotect_code(self, protected_file: Path, output_dir: Path, password: str) -> bool:
        """
        Desprotege código usando el método detectado automáticamente

        Args:
            protected_file: Archivo protegido
            output_dir: Directorio de salida
            password: Contraseña/licencia para desprotección
        """
        ...

    def detect_protection_method(self, protected_file: Path) -> Optional[str]:
        """Detecta el método de protección usado en un archivo"""
        ...

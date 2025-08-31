"""
Infraestructura - Servicio de encriptación simple
"""

import json
import logging
import tarfile
from base64 import urlsafe_b64decode, urlsafe_b64encode
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from ..domain.security_service import EncryptionProtocol


class SimpleEncryptionService(EncryptionProtocol):
    """Implementación de encriptación simple usando Fernet"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "cryptography package is required for encryption features. "
                "Install with: pip install cryptography"
            )

    def encrypt_directory(self, source_dir: Path, output_file: Path, password: str) -> bool:
        """
        Encripta un directorio completo en un archivo protegido

        Args:
            source_dir: Directorio fuente a encriptar
            output_file: Archivo encriptado de salida
            password: Contraseña para la encriptación

        Returns:
            bool: True si la encriptación fue exitosa
        """
        try:
            # Asegurar que el directorio de salida existe
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Generar clave de encriptación desde contraseña
            salt = b"sincpro_compiler_salt_2025"  # Salt fijo para reproducibilidad
            fernet = self._generate_fernet_key(password, salt)

            # Crear archivo tar temporal en memoria
            import io

            tar_buffer = io.BytesIO()

            with tarfile.open(mode="w:gz", fileobj=tar_buffer) as tar:
                # Agregar todos los archivos del directorio
                files_added = 0
                for file_path in self._walk_directory(source_dir):
                    if file_path.is_file():
                        # Calcular ruta relativa
                        relative_path = file_path.relative_to(source_dir)

                        # Agregar archivo al tar
                        tar.add(file_path, arcname=relative_path)
                        files_added += 1

                        self.logger.debug(f"Agregado al archivo: {relative_path}")

            # Obtener datos del tar
            tar_data = tar_buffer.getvalue()
            tar_buffer.close()

            # Encriptar los datos
            encrypted_data = fernet.encrypt(tar_data)

            # Crear metadata
            metadata = {
                "method": "encrypt",
                "salt": urlsafe_b64encode(salt).decode("utf-8"),
                "files_count": files_added,
            }

            # Escribir archivo final con metadata y datos encriptados
            with open(output_file, "wb") as f:
                # Escribir metadata como JSON seguido de separador
                metadata_json = json.dumps(metadata).encode("utf-8")
                f.write(len(metadata_json).to_bytes(4, "big"))
                f.write(metadata_json)
                f.write(b"---SINCPRO_SEPARATOR---")
                f.write(encrypted_data)

            self.logger.info(
                f"Encriptación completada: {files_added} archivos en {output_file}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error durante encriptación: {e}")
            return False

    def decrypt_file(self, encrypted_file: Path, output_dir: Path, password: str) -> bool:
        """
        Desencripta un archivo protegido

        Args:
            encrypted_file: Archivo encriptado
            output_dir: Directorio donde extraer
            password: Contraseña para desencriptación

        Returns:
            bool: True si la desencriptación fue exitosa
        """
        try:
            # Verificar que el archivo existe
            if not encrypted_file.exists():
                self.logger.error(f"Archivo no encontrado: {encrypted_file}")
                return False

            # Crear directorio de salida
            output_dir.mkdir(parents=True, exist_ok=True)

            # Leer archivo encriptado
            with open(encrypted_file, "rb") as f:
                # Leer tamaño de metadata
                metadata_size = int.from_bytes(f.read(4), "big")

                # Leer metadata
                metadata_json = f.read(metadata_size)
                metadata = json.loads(metadata_json.decode("utf-8"))

                # Leer separador
                separator = f.read(len(b"---SINCPRO_SEPARATOR---"))
                if separator != b"---SINCPRO_SEPARATOR---":
                    raise ValueError("Formato de archivo inválido")

                # Leer datos encriptados
                encrypted_data = f.read()

            # Generar clave de desencriptación
            salt = urlsafe_b64decode(metadata["salt"].encode("utf-8"))
            fernet = self._generate_fernet_key(password, salt)

            # Desencriptar datos
            try:
                decrypted_data = fernet.decrypt(encrypted_data)
            except Exception:
                self.logger.error("Contraseña incorrecta o archivo corrupto")
                return False

            # Extraer archivo tar
            import io

            tar_buffer = io.BytesIO(decrypted_data)

            with tarfile.open(mode="r:gz", fileobj=tar_buffer) as tar:
                tar.extractall(output_dir)
                files_extracted = len(tar.getnames())

            tar_buffer.close()

            self.logger.info(
                f"Desencriptación completada: {files_extracted} archivos extraídos"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error durante desencriptación: {e}")
            return False

    def _generate_fernet_key(self, password: str, salt: bytes):
        """
        Genera una clave Fernet desde contraseña usando PBKDF2

        Args:
            password: Contraseña del usuario
            salt: Salt para la derivación de clave

        Returns:
            Fernet: Instancia de Fernet para encriptación/desencriptación
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography package is required")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        return Fernet(key)

    def _walk_directory(self, directory: Path) -> list[Path]:
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

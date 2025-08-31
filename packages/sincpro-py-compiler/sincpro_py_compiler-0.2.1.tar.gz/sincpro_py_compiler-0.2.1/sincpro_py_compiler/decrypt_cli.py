#!/usr/bin/env python3
"""
CLI para desproteger código compilado de SincPro Python Compiler
"""

import argparse
import logging
from pathlib import Path

from .infrastructure.security_manager import SecurityManager


def main():
    """Punto de entrada para el CLI de desprotección"""
    parser = argparse.ArgumentParser(
        description="SincPro Python Compiler - Desprotege código compilado",
        epilog="Ejemplo: sincpro-decrypt ./codigo_protegido.zip --password mi_licencia -o ./codigo",
    )

    parser.add_argument("source", help="Archivo protegido a desproteger")
    parser.add_argument("-o", "--output", required=True, help="Directorio de salida")
    parser.add_argument(
        "--password", required=True, help="Contraseña/licencia para desproteger"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Mostrar información detallada"
    )

    args = parser.parse_args()

    # Configurar logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    # Validar archivos
    source_file = Path(args.source)
    if not source_file.exists():
        print(f"❌ Archivo no encontrado: {source_file}")
        exit(1)

    output_dir = Path(args.output)

    # Crear manager de seguridad
    security_manager = SecurityManager()

    # Detectar método de protección
    method = security_manager.detect_protection_method(source_file)
    if not method:
        print("❌ No se pudo detectar el método de protección del archivo")
        exit(1)

    print(f"🔍 Método de protección detectado: {method}")
    print(f"🔓 Desprotegiendo código...")

    # Desproteger código
    success = security_manager.unprotect_code(
        protected_file=source_file, output_dir=output_dir, password=args.password
    )

    if success:
        print(f"🎉 Código desprotegido exitosamente en: {output_dir}")
    else:
        print("❌ Error desprotegiendo código. Verifique la contraseña.")
        exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CLI para SincPro Python Compiler - Arquitectura limpia
"""

from .infrastructure.python_compiler import PythonCompiler


def main():
    """Punto de entrada principal para el CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        description="SincPro Python Compiler - Compila .py a .pyc y copia el resto",
        epilog="Ejemplo: sincpro-compile ./mi_proyecto -o ./compiled -t odoo",
    )

    parser.add_argument("source", nargs="?", help="Directorio fuente a compilar")
    parser.add_argument("-o", "--output", help="Directorio de salida (default: ./compiled)")
    parser.add_argument(
        "-t",
        "--template",
        choices=["basic", "django", "odoo"],
        default="basic",
        help="Template de exclusión (default: basic)",
    )
    parser.add_argument(
        "-e", "--exclude-file", help="Archivo custom de exclusiones (.sincpro_exclude)"
    )
    parser.add_argument(
        "--remove-py",
        action="store_true",
        help=argparse.SUPPRESS,  # Ocultar esta opción hasta que esté completamente implementada
    )
    parser.add_argument(
        "--list-templates", action="store_true", help="Mostrar templates disponibles y salir"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Mostrar información detallada"
    )

    # Argumentos para seguridad (compresión/encriptación)
    parser.add_argument(
        "--compress", action="store_true", help="Comprimir código compilado con contraseña"
    )
    parser.add_argument(
        "--encrypt", action="store_true", help="Encriptar código compilado con contraseña"
    )
    parser.add_argument(
        "--password", help="Contraseña/licencia para proteger el código compilado"
    )
    parser.add_argument(
        "--copy-faithful-file",
        help="Archivo con patrones de copia fiel (uno por línea)",
    )

    args = parser.parse_args()

    # Configurar nivel de logging
    import logging

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s - %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    # Crear instancia del compilador (arquitectura actual)
    compiler = PythonCompiler()

    # Mostrar templates si se solicita
    if args.list_templates:
        templates = ["basic", "django", "odoo"]
        print("📋 Templates disponibles:")
        for template in templates:
            print(f"  - {template}")
        return

    # Validar que se haya proporcionado el directorio fuente
    if not args.source:
        parser.error("Se requiere especificar el directorio fuente")

    # Validar argumentos de seguridad
    security_methods = [args.compress, args.encrypt]
    if sum(security_methods) > 1:
        parser.error("Solo se puede usar un método de seguridad: --compress o --encrypt")

    use_security = any(security_methods)
    if use_security and not args.password:
        parser.error("Se requiere --password cuando se usa --compress o --encrypt")

    # Directorio de salida por defecto
    output_dir = args.output or "./compiled"

    # Ejecutar compilación
    success = compiler.compile_project(
        source_dir=args.source,
        output_dir=output_dir,
        template=args.template,
        exclude_file=args.exclude_file,
        remove_py=args.remove_py,
        copy_faithful_file=args.copy_faithful_file,
    )

    if not success:
        print("❌ Error en la compilación")
        exit(1)

    # Aplicar seguridad si se solicitó
    if use_security:
        from pathlib import Path

        from .infrastructure.security_manager import SecurityManager

        security_manager = SecurityManager()

        # Determinar método y archivo de salida
        if args.compress:
            method = "compress"
            protected_file = Path(output_dir).parent / f"{Path(output_dir).name}.zip"
        else:  # encrypt
            method = "encrypt"
            protected_file = Path(output_dir).parent / f"{Path(output_dir).name}.enc"

        print(f"🔒 Aplicando protección ({method})...")

        security_success = security_manager.protect_compiled_code(
            compiled_dir=Path(output_dir),
            output_file=protected_file,
            password=args.password,
            method=method,
        )

        if security_success:
            print(f"🎉 Código protegido exitosamente: {protected_file}")

            # Opcional: eliminar directorio no protegido
            import shutil

            try:
                shutil.rmtree(output_dir)
                print(f"📁 Directorio temporal eliminado: {output_dir}")
            except Exception as e:
                print(f"⚠️  No se pudo eliminar directorio temporal: {e}")
        else:
            print("❌ Error aplicando protección")
            exit(1)
    else:
        print("🎉 Compilación exitosa!")


if __name__ == "__main__":
    main()

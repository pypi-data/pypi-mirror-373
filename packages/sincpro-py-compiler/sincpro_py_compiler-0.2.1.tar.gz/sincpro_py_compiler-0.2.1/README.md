# SincPro Python Compiler

Una herramienta simple y efectiva para compilar proyectos Python (.py → .pyc) y distribuir código compilado de forma segura.

## 🎯 Propósito

- **Compilar archivos .py a .pyc** para distribución segura del código
- **Copiar archivos no-Python tal como están** (XML, JS, TXT, etc.)
- **Excluir archivos específicos** según el tipo de proyecto
- **Ocultar código fuente** para distribución a clientes

## ⚡ Instalación

```bash
pip install sincpro-py-compiler
```

O desde el código fuente:

```bash
git clone https://github.com/Sincpro-SRL/sincpro_py_compiler.git
cd sincpro_py_compiler
poetry install
```

## 🚀 Uso Rápido

### Comandos básicos

```bash
# Compilar proyecto básico
sincpro-compile ./mi_proyecto

# Especificar directorio de salida
sincpro-compile ./mi_proyecto -o ./compilado

# Usar template para Django
sincpro-compile ./mi_django_app -t django

# Usar template para Odoo
sincpro-compile ./mi_addon_odoo -t odoo

# Ver templates disponibles
sincpro-compile --list-templates
```

### 🔒 Protección del Código Compilado (Nuevo Feature)

**SincPro Python Compiler** ahora incluye funcionalidades de seguridad para proteger tu código compilado mediante compresión con contraseña o encriptación simple. Esto es especialmente útil para la distribución comercial donde necesitas una licencia/contraseña para acceder al código.

#### Compresión con Contraseña

```bash
# Compilar y comprimir con contraseña
sincpro-compile ./mi_proyecto --compress --password "mi_licencia_comercial"

# Resultado: mi_proyecto_compilado.zip (protegido)
```

#### Encriptación Simple

```bash
# Compilar y encriptar con contraseña
sincpro-compile ./mi_proyecto --encrypt --password "clave_secreta"

# Resultado: mi_proyecto_compilado.enc (encriptado)
```

#### Desproteger Código

Para usar código protegido, utiliza el comando de desprotección:

```bash
# Descomprimir código protegido
sincpro-decrypt ./codigo_protegido.zip --password "mi_licencia_comercial" -o ./codigo_desprotegido

# Desencriptar código protegido  
sincpro-decrypt ./codigo_protegido.enc --password "clave_secreta" -o ./codigo_desprotegido
```

#### Ventajas de la Protección

- **Distribución Segura**: El código compilado no puede ser accedido sin la contraseña/licencia
- **Control de Licencias**: Cada cliente necesita su propia contraseña para ejecutar el código
- **Protección Comercial**: Impide el acceso casual al código .pyc
- **Flexibilidad**: Elige entre compresión (más compatible) o encriptación (más segura)

### 📦 Copias fieles por template (Nuevo Feature)

A partir de la versión actual, SincPro Python Compiler permite definir archivos y carpetas que serán **copiados fielmente** (sin compilar ni excluir) según el template seleccionado.

Por ejemplo, en el template `odoo`, los siguientes archivos y carpetas se copian tal cual al directorio de salida:

- `__manifest__.py`
- `__openerp__.py`
- `static/`
- `data/`
- `demo/`
- `security/`

Esto es útil para mantener la integridad de archivos requeridos por Odoo y otros frameworks, evitando su compilación o exclusión.

### Opciones avanzadas de copia fiel

Puedes definir archivos y carpetas adicionales para copiar fielmente usando la opción:

```bash
sincpro-compile ./mi_proyecto --copy-faithful-file mi_copias_fieles.txt
```

El archivo debe contener un patrón por línea, por ejemplo:

```
# Copias fieles personalizadas
config.json
assets/
logo.png
```

Estos patrones se suman a los definidos por el template seleccionado.

### Copia fiel usando patrones directos

Además de usar archivos de patrones, puedes pasar patrones directos o una lista separada por comas con la opción:

```bash
sincpro-compile ./mi_addon_odoo --copy-faithful-file __manifest__.py -o ./dist
```

O múltiples patrones:

```bash
sincpro-compile ./mi_addon_odoo --copy-faithful-file "__manifest__.py,config.json,logo.png" -o ./dist
```

Esto copiará fielmente los archivos y carpetas indicados, sin necesidad de crear un archivo de patrones.

También puedes seguir usando archivos de texto o archivos Python (.py) con la variable `COPY_FAITHFUL_PATTERNS` para definir múltiples patrones.

### Ejemplo de uso

```bash
sincpro-compile ./mi_addon_odoo -t odoo
```

En este caso, los archivos `.py` se compilan a `.pyc`, los archivos definidos como "copias fieles" se copian tal cual, y el resto se excluye según el template.

Puedes personalizar los templates o agregar tus propios patrones en la carpeta `resources/exclude_patterns/`.

### Uso con diferentes tipos de proyecto

#### Proyecto Python básico

```bash
sincpro-compile ./mi_app -t basic
```

#### Proyecto Django

```bash
sincpro-compile ./mi_django_project -t django -o ./dist
```

#### Addon Odoo

```bash
sincpro-compile ./mi_addon -t odoo -o ./compilado
```

## 📋 Templates Disponibles

### `basic` - Proyecto Python básico

Excluye:

- `__pycache__/`, `*.pyc`
- `.git/`, `.venv/`, `venv/`, `env/`
- Archivos de log y temporales
- Archivos de configuración de IDEs

### `django` - Proyecto Django

Incluye exclusiones básicas más:

- `migrations/`
- `static/`, `media/`
- `db.sqlite3`

### `odoo` - Addon Odoo

Incluye exclusiones básicas más:

- `__manifest__.py`, `__openerp__.py`
- `static/`, `data/`, `demo/`
- `security/`

## 🔧 Opciones Avanzadas

### Archivo de exclusiones personalizado

Crea un archivo con patrones de exclusión (uno por línea):

```text
# Mi archivo de exclusiones personalizadas
*.log
temp/
config/secret.py
docs/
```

Úsalo con:

```bash
sincpro-compile ./proyecto -e mi_exclusiones.txt
```

### Opciones del CLI

```bash
sincpro-compile [directorio] [opciones]

Opciones:
  -o, --output DIR          Directorio de salida (default: ./compiled)
  -t, --template TEMPLATE   Template: basic, django, odoo (default: basic)
  -e, --exclude-file FILE   Archivo personalizado de exclusiones
  --list-templates         Mostrar templates disponibles
  -v, --verbose           Mostrar información detallada
  -h, --help              Mostrar ayuda
```

## 💡 Ejemplos Prácticos

### Distribuir una aplicación Python

```bash
# Compilar y generar distribución limpia
sincpro-compile ./mi_app -o ./dist -t basic
```

### Preparar addon Odoo para cliente

```bash
# Compilar addon excluyendo manifests y archivos de datos
sincpro-compile ./mi_addon -t odoo -o ./cliente_dist
```

### Proyecto Django para producción

```bash
# Compilar excluyendo migraciones y archivos estáticos
sincpro-compile ./mi_web -t django -o ./produccion
```

## 🛠 Uso Programático

```python
from sincpro_py_compiler.infrastructure.python_compiler import PythonCompiler

# Crear instancia del compilador
compiler = PythonCompiler()

# Compilar proyecto
success = compiler.compile_project(
    source_dir="./mi_proyecto",
    output_dir="./compilado",
    template="basic"
)

if success:
    print("¡Compilación exitosa!")
```

## 📁 Estructura de Salida

El compilador mantiene la estructura original del proyecto:

```
mi_proyecto/
├── app.py
├── utils.py
├── config.xml
└── static/
    └── style.css

# Después de compilar:
compilado/
├── app.pyc          # Compilado
├── utils.pyc        # Compilado  
├── config.xml       # Copiado tal como está
└── static/
    └── style.css    # Copiado tal como está
```

## ⚠️ Limitaciones

- Solo compila archivos `.py` a `.pyc`
- No es cifrado ni ofuscación avanzada
- Los archivos `.pyc` pueden ser descompilados
- Para protección avanzada considerar PyArmor

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un Pull Request

## � Documentación

- **[Arquitectura del Sistema](docs/ARCHITECTURE.md)** - Detalles técnicos y diseño
- **[Guía de Deployment](docs/DEPLOYMENT.md)** - Instrucciones de lanzamiento e instalación
- **[Tests](tests/)** - Suite de tests completa con casos de uso reales

## �📄 Licencia

MIT License - ver archivo LICENSE para detalles.

## 🏢 Empresa

Desarrollado por **Sincpro SRL** para distribución segura de código Python.

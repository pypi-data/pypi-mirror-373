# Flask-LiveReload

Una extensión de Flask que proporciona recarga en vivo de las páginas web cuando los archivos de plantilla o estáticos cambian. Ideal para acelerar el desarrollo al eliminar la necesidad de recargar manualmente el navegador después de cada cambio.

## 🌟 Características

- **🔄 Recarga automática**: Monitorea los directorios `templates` y `static` en busca de cambios en los archivos.
- **⚡ Integración sencilla**: Se integra fácilmente en cualquier aplicación Flask.
- **🚀 Ligera**: Solo depende de Flask y watchdog, sin dependencias externas pesadas.
- **📡 Eficiente**: Utiliza Server-Sent Events (SSE) para notificar al navegador de los cambios.
- **🔧 Configurable**: Soporte para patrones personalizados de observación e ignorar archivos.
- **🛡️ Robusta**: Manejo de errores mejorado y logging detallado.

## 📦 Instalación

Puedes instalar Flask-LiveReload directamente desde PyPI usando pip:

```bash
pip install Flask-LiveReload
```

## 🚀 Uso

### Configuración Básica

Para empezar a usar Flask-LiveReload, simplemente importa la clase `LiveReload` y pásale tu aplicación Flask.

```python
from flask import Flask, render_template
from flask_livereload import LiveReload

app = Flask(__name__)
app.debug = True  # ⚠️ IMPORTANTE: Solo funciona en modo debug
livereload = LiveReload(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

### Configuración Avanzada

Puedes personalizar qué archivos observar e ignorar:

```python
from flask import Flask, render_template
from flask_livereload import LiveReload

app = Flask(__name__)
app.debug = True

# Configurar patrones personalizados
app.config["LIVERELOAD_WATCH_PATTERNS"] = [
    "statics/**/*.html",
    "statics/**/*.js",
    "statics/**/*.css",
    "templates/**/*.html",
]

app.config["LIVERELOAD_IGNORE_PATTERNS"] = [
    "__pycache__",
    ".venv",
    ".git",
    ".pytest_cache",
    "*.pyc",
    "*.pyo",
    "*.log",
    ".DS_Store",
    "node_modules",
]

livereload = LiveReload(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

## 🧠 ¿Cómo funciona?

Flask-LiveReload inyecta un pequeño script de JavaScript en tus páginas HTML. Este script se conecta a un endpoint de Server-Sent Events (SSE) en `/_livereload`. En el lado del servidor, un observador de archivos monitorea los directorios configurados. Cuando se detecta un cambio, se envía un mensaje al navegador a través del SSE, lo que provoca que la página se recargue.

## ⚙️ Configuración

### Variables de Entorno

```bash
# Nivel de logging (DEBUG, INFO, WARNING, ERROR)
export LOG_LEVEL=INFO
```

### Opciones de Configuración de Flask

```python
# Patrones de archivos a observar (opcional)
app.config["LIVERELOAD_WATCH_PATTERNS"] = [
    "statics/**/*.html",    # Todos los HTML en statics y subdirectorios
    "statics/**/*.js",      # Todos los JS en statics y subdirectorios
    "templates/**/*.html",  # Todos los HTML en templates y subdirectorios
]

# Patrones de archivos a ignorar (opcional)
app.config["LIVERELOAD_IGNORE_PATTERNS"] = [
    "__pycache__",
    ".venv",
    ".git",
    "*.pyc",
    "node_modules",
]
```

## 🐛 Solución de Problemas

### Problemas Comunes

1. **No se recarga automáticamente**: 
   - Verifica que `app.debug = True`
   - Revisa los logs para errores
   - Asegúrate de que los archivos estén en los directorios correctos

2. **Error de importación**:
   - Verifica que el paquete esté instalado correctamente
   - Asegúrate de usar el token correcto si es un repositorio privado

3. **Problemas con patrones**:
   - Los patrones usan sintaxis glob
   - Usa `./` para rutas relativas al directorio de la aplicación

### Logging

Habilita logging detallado para debugging:

```bash
export LOG_LEVEL=DEBUG
```

## 📚 Documentación Adicional

Para ejemplos más detallados y guías de uso, consulta:
- `examples/README.md` - Guía completa de uso
- `examples/local_development_guide.md` - Desarrollo local
- `examples/standalone_example.py` - Ejemplo básico
- `examples/custom_watch_patterns_example.py` - Ejemplo con patrones personalizados

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si tienes alguna idea, sugerencia o informe de error, por favor abre un issue o envía un pull request.

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

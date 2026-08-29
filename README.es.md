# 🤖 vibecoding-machine

**vibecoding-machine** es un asistente de programación impulsado por IA que conecta un gran modelo de lenguaje (LLM) con herramientas reales para trabajar en GitHub. Chatea con él en tu terminal o en una interfaz web moderna (Streamlit), y él planificará y ejecutará tareas de varios pasos por ti: crear repositorios, gestionar archivos, configurar licencias, buscar en la web y ejecutar código en más de 20 lenguajes de programación.

El asistente construye su comportamiento a partir de tus preferencias (estilo de código, uso de Markdown, lenguajes preferidos), sigue reglas de seguridad y te muestra cada paso que da.

[**English**](README.md) | [**Русский**](README.ru.md) | [**Español**](README.es.md) | [**中文**](README.zh.md)

## ✨ Características

- 🧠 **Agente basado en LLM** — utiliza llamadas a funciones (function calling) para planificar y completar tareas de varios pasos a partir de una sola instrucción.
- 💬 **Dos interfaces** — un chat de terminal con colores (`terminal.py`) y una interfaz web moderna (`app.py`, construida con Streamlit).
- 🔧 **Herramientas de GitHub** — crear repositorios, leer/escribir/eliminar archivos y listar el contenido de un repositorio.
- 📜 **Gestor de licencias** — establece automáticamente licencias MIT, Apache-2.0, GPL-3.0, MPL-2.0 o CC0.
- 🌐 **Búsqueda web** — búsqueda integrada mediante la API de Langsearch.
- 🕒 **Herramienta de fecha/hora** — obtén la fecha y hora actuales en cualquier zona horaria.
- 🧪 **Ejecutor de código** — ejecuta código en más de 20 lenguajes (backend Judge0) con salida stdout/stderr.
- ⚙️ **Configuración en vivo** — cambia el modelo, los límites de operaciones, las preferencias y el idioma con `/config`.
- 🌍 **Interfaz localizada** — 13 idiomas disponibles.
- 🐳 **Soporte Docker** — imagen de contenedor y flujo de trabajo de publicación automática.

## 🛠️ Cómo funciona

1. Envías un mensaje desde la terminal o la interfaz web.
2. El asistente llama al LLM con un prompt de sistema generado a partir de tus preferencias en `ai/config.py`.
3. Si el modelo decide invocar una herramienta, esta se ejecuta y su resultado se devuelve al modelo.
4. El bucle se repite hasta que el modelo produce una respuesta final (hasta `model_operation_limit` iteraciones).

## 📦 Requisitos

- Python 3.10+ (se recomienda 3.13; hay un Python portable para Windows incluido en `python/`)
- Una clave de API y un endpoint de LLM compatible con OpenAI
- Una clave de API de Langsearch para la búsqueda web (opcional, pero recomendada)

## 🔧 Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/Snupkindeker/vibecoding-machine.git
cd vibecoding-machine

# 2. Crea y activa un entorno virtual (recomendado)
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Crea un archivo .env con tus claves
AI_API_KEY=your_llm_api_key
AI_API_ENDPOINT=https://your-llm-endpoint/v1
LANGSEARCH_KEY=your_langsearch_api_key
```

En Windows también puedes usar los lanzadores listos: `run.bat`, `run.ps1` o `start_app.bat`.

## ⚙️ Configuración

Los ajustes principales están en [`ai/config.py`](ai/config.py):

| Ajuste | Descripción | Valor por defecto |
| --- | --- | --- |
| `model_name` | El modelo LLM usado en el chat | `deepseek-v4-flash-0731` |
| `model_operation_limit` | Máx. de llamadas a herramientas + pasos de razonamiento por instrucción | `25` |
| `github_username` | Tu nombre de usuario de GitHub (necesario para las herramientas de GitHub) | `Snupkindeker` |
| `coding_case` | `snake`, `camel` o `pascal` | `snake` |
| `use_markdown` | Si la IA debe usar Markdown | `True` |
| `preferred_languages` | Lenguajes de programación preferidos (vacío = cualquiera) | `[]` |
| `language` | Idioma de la interfaz: `en`, `ru`, `es`, ... | `en` |

## 🚀 Uso

### 💻 Interfaz de terminal

```bash
python terminal.py
```

### 🌐 Interfaz web (Streamlit)

```bash
streamlit run app.py
```

### 🚀 Ambos a la vez

```bash
python main.py
```

Esto inicia la aplicación Streamlit en segundo plano y el chat de terminal en primer plano. Pulsa `Ctrl+C` o escribe `/stop` para salir.

## ⌨️ Comandos

| Comando | Descripción |
| --- | --- |
| `/help` | Mostrar la ayuda |
| `/stop` | Salir del chat |
| `/wipe` | Borrar el historial de la conversación |
| `/config` | Mostrar la configuración actual |
| `/config check` | Validar la configuración |
| `/config reset` | Restablecer la configuración a los valores por defecto |
| `/config <clave> <valor>` | Cambiar un ajuste concreto |
| `/save <nombre>` | Guardar la conversación actual |
| `/load <nombre>` | Cargar una conversación guardada |
| `/del <nombre>` | Eliminar una conversación guardada |

Las conversaciones guardadas se almacenan como JSON en `ai/dialogs/`.

## 🧰 Herramientas de la IA

| Herramienta | Descripción |
| --- | --- |
| `web_search` | Buscar en la web |
| `get_datetime` | Obtener la fecha y hora actuales en cualquier zona horaria |
| `create_repo` | Crear un repositorio de GitHub (privado por defecto) |
| `set_license` | Establecer una licencia: MIT, Apache-2.0, GPL-3.0, MPL-2.0, CC0 |
| `create_file` | Crear un archivo en un repositorio |
| `write_file` | Editar un archivo en un repositorio |
| `read_file` | Leer un archivo de un repositorio |
| `delete_file` | Eliminar un archivo de un repositorio |
| `get_file_list` | Listar el contenido de un repositorio |
| `run_code` | Ejecutar código en más de 20 lenguajes (stdin/stdout/stderr) |

## 🌍 Localización

La interfaz está disponible en **13 idiomas** (`locales/*.json`): inglés, ruso, español, francés, chino, árabe, alemán, coreano, portugués, japonés, hindi, bengalí e italiano.

Cambia el idioma con `/config language <código>` o desde la barra lateral de la aplicación web.

## 🐳 Docker

Se incluye un [`Dockerfile`](Dockerfile) basado en `python:3.13-slim`, y `.github/workflows/docker-publish.yml` publica la imagen automáticamente.

```bash
docker build -t vibecoding-machine .
docker run -p 8501:8501 --env-file .env vibecoding-machine
```

Para ejecutar solo la interfaz web dentro de un contenedor, sobrescribe el comando:

```bash
docker run -p 8501:8501 --env-file .env vibecoding-machine streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📁 Estructura del proyecto

```
.
├── ai/                  # Núcleo de IA: configuración, herramientas, ciclo, localización, diálogos
├── github_tools/        # Envoltorios de la API de GitHub
├── licenses/            # Plantillas de licencias
├── locales/             # Traducciones de la interfaz (13 idiomas)
├── exceptions/          # Excepciones personalizadas
├── python/              # Python 3.13 portable (Windows)
├── app.py               # Interfaz web con Streamlit
├── terminal.py          # Interfaz de terminal
├── main.py              # Inicia web + terminal a la vez
├── palette.py           # Colores de la terminal
├── logger_setup.py      # Configuración de registro (logging)
├── requirements.txt     # Dependencias de Python
├── Dockerfile           # Imagen de contenedor
├── run.bat / run.ps1    # Lanzadores de Windows
└── start_app.bat        # Lanzador de Streamlit (Windows)
```

## 📄 Licencia

Distribuido bajo la [licencia MIT](LICENSE). Copyright © 2026 Snupkindeker.
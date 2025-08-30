from sys import version_info

# Deployment
PYTHON_VERSION = f"{version_info.major}.{version_info.minor}"
DOCKER_BASE_IMAGE_URL = "debian:bookworm-slim"
INCLUDE = ["./*", "main.py", "cerebrium.toml"]
EXCLUDE = [".*"]
SHELL_COMMANDS = []
PRE_BUILD_COMMANDS = []
DISABLE_AUTH = True

# Custom Runtime
ENTRYPOINT = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
PORT = 8000
HEALTHCHECK_ENDPOINT = ""
READYCHECK_ENDPOINT = ""
DOCKERFILE_PATH = ""

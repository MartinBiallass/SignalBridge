import os

# Basisverzeichnis des Projekts
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Prüfen, ob die App in einer Cloud-Umgebung ausgeführt wird
IS_CLOUD_ENV = os.getenv("CLOUD_ENV", "false").lower() == "true"

# Datenpfade für lokale Umgebung
if not IS_CLOUD_ENV:
    SIGNALGEBER_DB = os.path.join(BASE_DIR, "data", "signalgeber.json")
    PERFORMANCE_DB = os.path.join(BASE_DIR, "data", "performance.json")

# Datenpfade für Cloud-Umgebung (z. B. AWS S3 oder Azure Blob Storage)
else:
    SIGNALGEBER_DB = os.getenv("SIGNALGEBER_DB_URL")  # URL oder Pfad aus Umgebungsvariable
    PERFORMANCE_DB = os.getenv("PERFORMANCE_DB_URL")  # URL oder Pfad aus Umgebungsvariable

# Zusätzliche Konfigurationen
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

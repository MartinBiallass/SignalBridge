import os

# Basisverzeichnis des Projekts
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Datenpfade
SIGNALGEBER_DB = os.path.join(BASE_DIR, "data", "signalgeber.json")
PERFORMANCE_DB = os.path.join(BASE_DIR, "data", "performance.json")

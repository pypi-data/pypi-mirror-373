from pathlib import Path
from importlib.metadata import version

try:
    __version__ = version("avst")
except Exception:
    __version__ = "unknown"

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
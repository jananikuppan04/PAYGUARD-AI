import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "app"
for p in [str(BASE_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.models import *

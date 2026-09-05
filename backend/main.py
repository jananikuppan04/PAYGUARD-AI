import sys
from pathlib import Path

# Add backend and backend/app to sys.path
BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "app"
for p in [str(BASE_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

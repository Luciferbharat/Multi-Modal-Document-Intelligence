
import os
import sys
import subprocess
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

def ensure_env():
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        raise RuntimeError(".env file missing. Create it with GROQ_API_KEY etc.")

    load_dotenv(env_path)

def main():
    ensure_env()

    # Just start uvicorn for FastAPI app in backend.main:app
    # Index build hum API se ya first call pe karenge.
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()

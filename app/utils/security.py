import os
import secrets
from pathlib import Path

from dotenv import load_dotenv, set_key


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


def get_or_create_secret(name):
    
    value = os.getenv(name)

    if not value:
        value = secrets.token_urlsafe(32)

        set_key(
            str(ENV_FILE),
            name,
            value
        )

        os.environ[name] = value

    return value

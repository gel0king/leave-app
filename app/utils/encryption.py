import os
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key


BASE_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

def get_fernet():
    key = os.getenv("FERNET_KEY")

    # Generate a key on first startup
    if not key:
        key = Fernet.generate_key().decode()
        set_key(
            str(ENV_FILE),
            "FERNET_KEY",
            key
        )

        os.environ["FERNET_KEY"] = key

    return Fernet(key.encode())


fernet = get_fernet()


def encrypt(value):
    if value is None or value == "":
        return None

    return fernet.encrypt(value.encode()).decode()


def decrypt(value):
    if value is None or value == "":
        return None

    return fernet.decrypt(value.encode()).decode()

import os
import secrets

from dotenv import load_dotenv, set_key

from app.utils.config import ENV_PATH


load_dotenv(ENV_PATH)


def get_or_create_secret(name):
    value = os.getenv(name)

    if not value:
        value = secrets.token_urlsafe(32)

        ENV_PATH.parent.mkdir(parents=True, exist_ok=True)

        set_key(
            str(ENV_PATH),
            name,
            value
        )

        os.environ[name] = value

    return value

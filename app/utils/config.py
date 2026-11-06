
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


APP_DIR = get_app_dir()
CONFIG_PATH = APP_DIR / "config.json"
ENV_PATH = APP_DIR / ".env"


def load_environment():
    load_dotenv(ENV_PATH, override=True)


def _load_config(config_path=CONFIG_PATH):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        print(f"Couldn't find config file: {config_path}")
        return None

    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        return None


def _resolve_path(path_value, config_path=CONFIG_PATH):
    """
    Resolve a relative path relative to the directory containing
    config.json, rather than the current working directory.
    """
    path = Path(path_value)

    if not path.is_absolute():
        path = config_path.parent / path

    return path.resolve()


def get_database_uri():
    """
    Return the Neon PostgreSQL connection string.
    SQLite is no longer supported.
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. "
            "Configure your Neon PostgreSQL connection in .env."
        )

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    if not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError(
            "DATABASE_URL must use PostgreSQL with Psycopg 3."
        )

    return database_url


def get_database_engine_options():
    return {
        "pool_pre_ping": True,
        "pool_size": 3,
        "max_overflow": 2,
        "pool_timeout": 30,
    }


def get_form_path(config_path=CONFIG_PATH):
    config = _load_config(config_path)

    if config is None:
        return None

    form_path = _resolve_path(config["FORM"], config_path)

    if not form_path.exists():
        print(f"Warning: form template doesn't exist: {form_path}")

    return str(form_path)


def get_leave_requests_dir(config_path=CONFIG_PATH):
    config = _load_config(config_path)

    if config is None:
        return None

    requests_value = config.get("LEAVE_REQUESTS")

    if not requests_value:
        raise RuntimeError("LEAVE_REQUESTS is missing from config.json")

    requests_dir = _resolve_path(requests_value, config_path)

    requests_dir.mkdir(parents=True, exist_ok=True)

    return str(requests_dir)

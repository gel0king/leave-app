import json
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
    load_dotenv(ENV_PATH)


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


def get_db_path(config_path=CONFIG_PATH):
    config = _load_config(config_path)

    if config is None:
        return None

    db_path = _resolve_path(config["DATABASE"], config_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    return str(db_path)


def get_database_uri():
    db_path = get_db_path()

    if db_path is None:
        raise RuntimeError("Could not determine database path.")

    db_path = Path(db_path).as_posix()

    return f"sqlite:///{db_path}"


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

    requests_dir = _resolve_path(requests_value, config_path)

    requests_dir.mkdir(parents=True, exist_ok=True)

    return str(requests_dir)

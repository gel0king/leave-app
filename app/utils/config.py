import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "config.json"

def _load_config(config_path=CONFIG_PATH):
    try:
        with open(config_path, "r") as f:
            return json.load(f)

    except FileNotFoundError:
        print(f"Couldn't find config file: {config_path}")
        return None

    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        return None

def _resolve_path(relative_path):
    """Resolve a config-file path relative to the project root, regardless
    of the process's current working directory."""
    path = Path(relative_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path

def get_db_path(config_path=CONFIG_PATH):
    config = _load_config(config_path)
    if config is None:
        return None

    db_path = _resolve_path(config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return str(db_path)

def get_database_uri():
    db_path = get_db_path()
    return f"sqlite:///{Path(db_path).resolve()}"

def get_form_path(config_path=CONFIG_PATH):
    config = _load_config(config_path)
    if config is None:
        return None

    form_path = _resolve_path(config["FORM"])
    form_path.parent.mkdir(parents=True, exist_ok=True)

    return str(form_path)

def get_leave_requests_dir(config_path=CONFIG_PATH):
    config = _load_config(config_path)
    if config is None:
        return None

    requests_dir = _resolve_path(config.get("LEAVE_REQUESTS_DIR", "leave_requests"))
    requests_dir.mkdir(parents=True, exist_ok=True)

    return str(requests_dir)
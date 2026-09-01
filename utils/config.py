import json
import os

CONFIG_PATH = "./config.json"

def get_db_path(config_path=CONFIG_PATH):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        db_path = config["DATABASE"]

        # check for db file
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        return db_path

    except FileNotFoundError:
        print(f"Couldn't find config file: {config_path}")
        return None

    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        return None

def get_form_path(config_path=CONFIG_PATH):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        form_path = config["FORM"]

        # check for db file
        db_dir = os.path.dirname(os.path.abspath(form_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        return form_path

    except FileNotFoundError:
        print(f"Couldn't find config file: {config_path}")
        return None

    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        return None
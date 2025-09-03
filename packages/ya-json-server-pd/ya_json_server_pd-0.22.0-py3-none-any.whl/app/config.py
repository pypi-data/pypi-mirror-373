from dotenv import dotenv_values

_CONFIG = dotenv_values(".env")

if "APP_JSON_FILENAME" not in _CONFIG:
    _CONFIG["APP_JSON_FILENAME"] = "data/db.json"

DB_JSON_FILENAME = _CONFIG["APP_JSON_FILENAME"]

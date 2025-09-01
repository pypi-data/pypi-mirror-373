import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))


PYQQQ_API_URL = "https://qupiato.com/api"

PYQQQ_EVENT_WS_URL = "wss://pyqqq.net/events/ws"


def get_tiny_db_path():
    return os.getenv("TINY_DB_PATH", "db.json")


def get_pyqqq_api_key():
    return os.getenv("PYQQQ_API_KEY")


def get_credential_file_path():
    return os.path.expanduser("~/.qred")


def is_google_cloud_logging_enabled():
    return os.getenv("GOOGLE_CLOUD_LOGGING_ENABLED", "false") == "true"

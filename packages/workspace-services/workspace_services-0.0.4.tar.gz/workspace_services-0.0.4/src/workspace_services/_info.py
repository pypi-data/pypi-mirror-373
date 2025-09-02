import importlib.metadata

APP_NAME = "workspace_services"
__info__ = importlib.metadata.metadata(APP_NAME)

APP_SUMMARY = __info__.get("summary", "")
VERSION = __info__.get("version")
AUTHOR_EMAIL = __info__.get("author_email")

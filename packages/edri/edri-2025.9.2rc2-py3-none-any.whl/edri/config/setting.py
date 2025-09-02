from os import getenv
from typing import Literal

HEALTH_CHECK_TIMEOUT = int(getenv("EDRI_HEALTH_CHECK_TIMEOUT", 10))
HEALTH_CHECK_FAILURE_LIMIT = int(getenv("EDRI_HEALTH_CHECK_FAILURE_LIMIT", 3))
API_RESPONSE_TIMEOUT = int(getenv("EDRI_API_RESPONSE_TIMEOUT", 60))
ENVIRONMENT: Literal["development", "production"] = "production" if getenv("ENVIRONMENT") == "production" else "development"

SWITCH_KEY_LENGTH = int(getenv("EDRI_SWITCH_KEY_LENGTH ", 8))
SWITCH_HOST = getenv("EDRI_SWITCH_HOST", "localhost")
SWITCH_PORT = int(getenv("EDRI_SWITCH_PORT", 8899))

UPLOAD_FILES_PREFIX = getenv("EDRI_UPLOAD_FILES_PREFIX", "edri_")
UPLOAD_FILES_PATH = getenv("EDRI_UPLOAD_FILES_PATH", "/tmp/upload")

CACHE_TIMEOUT = int(getenv("EDRI_CACHE_TIMEOUT", 30))
CACHE_INFO_MESSAGE = int(getenv("EDRI_CACHE_INFO_MESSAGE", 60))

HOST = getenv("EDRI_HOST", "localhost")
PORT = int(getenv("EDRI_PORT", 8080))
SSL_KEY = getenv("EDRI_SSL_KEY")
SSL_CERTIFICATE = getenv("EDRI_SSL_CERTIFICATE")

TEMPLATE_PATH = getenv("EDRI_TEMPLATE_PATH", "templates")
ASSETS_PATH = getenv("EDRI_ASSETS_PATH", "assets")
MAX_BODY_SIZE = int(getenv("EDRI_MAX_BODY_SIZE", 4096 * 1024))
CHUNK_SIZE = int(getenv("EDRI_CHUNK_SIZE", 256 * 1024))

CORS_ORIGINS = getenv("EDRI_CORS_ORIGINS")
CORS_HEADERS = getenv("EDRI_CORS_HEADERS")
CORS_CREDENTIALS = bool(getenv("EDRI_CORS_CREDENTIALS", False))
CORS_MAX_AGE = getenv("EDRI_CORS_MAX_AGE", None)

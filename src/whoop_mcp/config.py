import os
from pathlib import Path

from dotenv import load_dotenv


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, override=True)


# --------------------------------------------------
# WHOOP OAuth configuration
# --------------------------------------------------

WHOOP_CLIENT_ID = (
    os.getenv("WHOOP_CLIENT_ID") or ""
).strip()

WHOOP_CLIENT_SECRET = (
    os.getenv("WHOOP_CLIENT_SECRET") or ""
).strip()

WHOOP_REDIRECT_URI = (
    os.getenv("WHOOP_REDIRECT_URI") or ""
).strip()


# --------------------------------------------------
# Public application host
# --------------------------------------------------
#
# Examples:
#
# Local:
#   localhost
#
# ngrok:
#   skeletal-extended-femur.ngrok-free.dev
#
# Production:
#   personal-whoop-mcp.up.railway.app
#
# Do not include "https://" or a trailing slash.
# --------------------------------------------------

PUBLIC_HOST = (
    os.getenv("PUBLIC_HOST") or "localhost"
).strip()


# Normalize accidental URL-style values so the rest
# of the application always gets only the hostname.
PUBLIC_HOST = (
    PUBLIC_HOST
    .removeprefix("https://")
    .removeprefix("http://")
    .rstrip("/")
)
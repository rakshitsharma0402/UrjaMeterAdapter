import os

from dotenv import load_dotenv

load_dotenv()


URJA_BASE_URL = os.getenv(
    "URJA_BASE_URL",
    "https://urja-ops.flockenergy.tech",
)

URJA_EMAIL = os.getenv("URJA_EMAIL")
URJA_PASSWORD = os.getenv("URJA_PASSWORD")



import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL: str = os.getenv("OPENF1_BASE_URL", "https://api.openf1.org/v1")
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
DEFAULT_YEAR: int = int(os.getenv("DEFAULT_YEAR", "2024"))
TOP_N_LAPS: int = int(os.getenv("TOP_N_LAPS", "5"))

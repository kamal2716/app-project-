"""Application configuration for CAMPUS IQ."""
from pathlib import Path

APP_NAME = "CAMPUS IQ"
APP_VERSION = "1.0.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
DB_PATH = DATA_DIR / "campus_iq.db"

WINDOW_SIZE = "1440x900"
MIN_WINDOW_SIZE = (1100, 720)

COLORS = {
    "navy": "#172554", "navy_light": "#243B70", "blue": "#3B82F6",
    "blue_soft": "#EAF2FF", "cyan": "#06B6D4", "green": "#16A36A",
    "green_soft": "#E8F7F0", "amber": "#D97706", "amber_soft": "#FFF5E5",
    "red": "#DC5252", "red_soft": "#FDECEC", "ink": "#172033",
    "muted": "#718096", "line": "#E7ECF3", "canvas": "#F5F7FB",
    "white": "#FFFFFF",
}

"""MediaMovarr - Organize downloaded media files according to Plex guidelines."""

__version__ = "1.0.0"
__author__ = "MediaMovarr Team"
__description__ = (
    "CLI tool to organize downloaded media files according to Plex guidelines"
)

from .classify import MediaType, classify_media
from .confidence_rules import apply_confidence_rules, get_default_confidence_rules
from .config import ConfigError, load_config
from .database import MediaMovarrDB, get_database
from .discovery import scan_for_media_folders
from .mover import MoveResult, move_media
from .renamer import get_renamed_path
from .tmdb_client import TMDbClient, create_tmdb_client

__all__ = [
    "load_config",
    "ConfigError",
    "classify_media",
    "MediaType",
    "scan_for_media_folders",
    "get_renamed_path",
    "move_media",
    "MoveResult",
    "TMDbClient",
    "create_tmdb_client",
    "apply_confidence_rules",
    "get_default_confidence_rules",
    "MediaMovarrDB",
    "get_database",
]

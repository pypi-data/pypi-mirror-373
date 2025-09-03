"""Configuration loading and validation for MediaMovarr."""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigError(Exception):
    """Configuration validation error."""

    pass


def expand_path(path: str) -> str:
    """Expand environment variables and resolve path."""
    expanded = os.path.expandvars(path)
    return str(Path(expanded).resolve())


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load and validate configuration from JSON file."""
    config_file = Path(config_path)

    if not config_file.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {e}") from e

    # Validate required fields
    required_fields = ["scan_dirs", "dest_dir"]
    for field in required_fields:
        if field not in config:
            raise ConfigError(f"Missing required config field: {field}")

    # Handle single scan_dir for backward compatibility
    if "scan_dir" in config and "scan_dirs" not in config:
        config["scan_dirs"] = [config["scan_dir"]]

    # Expand paths
    config["scan_dirs"] = [expand_path(path) for path in config["scan_dirs"]]
    config["dest_dir"] = expand_path(config["dest_dir"])

    # Validate scan directories exist
    for scan_dir in config["scan_dirs"]:
        if not Path(scan_dir).exists():
            raise ConfigError(f"Scan directory does not exist: {scan_dir}")

    # Validate destination directory
    dest_path = Path(config["dest_dir"])
    if not dest_path.exists():
        try:
            dest_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ConfigError(
                f"Cannot create destination directory {config['dest_dir']}: {e}"
            ) from e

    # Set defaults
    config.setdefault("tmdb_enabled", False)
    config.setdefault("verbose", False)
    config.setdefault("rules", {})
    config.setdefault(
        "confidence_thresholds", {"auto_process": 0.9, "require_confirmation": 0.5}
    )

    # Set default confidence rules if not provided
    if "confidence_rules" not in config:
        from .confidence_rules import get_default_confidence_rules

        config["confidence_rules"] = get_default_confidence_rules()

    # Validate confidence thresholds
    thresholds = config["confidence_thresholds"]
    if not isinstance(thresholds.get("auto_process"), (int, float)) or not (
        0 <= thresholds["auto_process"] <= 1
    ):
        raise ConfigError("auto_process threshold must be a number between 0 and 1")
    if not isinstance(thresholds.get("require_confirmation"), (int, float)) or not (
        0 <= thresholds["require_confirmation"] <= 1
    ):
        raise ConfigError(
            "require_confirmation threshold must be a number between 0 and 1"
        )
    if thresholds["auto_process"] < thresholds["require_confirmation"]:
        raise ConfigError(
            "auto_process threshold must be >= require_confirmation threshold"
        )

    # Validate TMDb settings
    if config.get("tmdb_enabled"):
        if not config.get("tmdb_api_key") and not config.get("tmdb_read_access_token"):
            raise ConfigError(
                "TMDb enabled but no API key or read access token provided"
            )

    return config


def get_default_config() -> Dict[str, Any]:
    """Get default configuration template."""
    from .confidence_rules import get_default_confidence_rules

    return {
        "scan_dirs": ["C:\\Downloads", "%USERPROFILE%\\Downloads"],
        "dest_dir": "D:\\Media",
        "tmdb_enabled": False,
        "tmdb_api_key": "",
        "tmdb_read_access_token": "",
        "confidence_thresholds": {"auto_process": 0.9, "require_confirmation": 0.5},
        "confidence_rules": get_default_confidence_rules(),
        "rules": {
            "tv_format": "{title}/Season {season:02d}/{title}.S{season:02d}E{episode:02d}",
            "movie_format": "{title} ({year})",
            "music_format": "{artist}/{album}/{track:02d} - {title}",
            "audiobook_format": "{author}/{title}/{chapter:02d} - {chapter_title}",
        },
        "file_extensions": {
            "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
            "audio": [".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a"],
            "subtitles": [".srt", ".vtt", ".ass", ".ssa", ".sub"],
        },
    }

"""Confidence rule processing for MediaMovarr."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .discovery import get_folder_info

logger = logging.getLogger(__name__)


def apply_confidence_rules(
    folder_path: Path,
    base_confidence: float,
    media_type: str,
    config: Dict[str, Any],
    tmdb_match: bool = False,
) -> Tuple[float, List[str]]:
    """
    Apply custom confidence rules to adjust the base confidence score.

    Args:
        folder_path: Path to the media folder
        base_confidence: Base confidence score from classification
        media_type: Detected media type
        config: Configuration dictionary
        tmdb_match: Whether TMDb found a match for this content

    Returns:
        Tuple of (adjusted_confidence, list_of_applied_rules)
    """
    confidence_rules = config.get("confidence_rules", [])
    if not confidence_rules:
        return base_confidence, []

    adjusted_confidence = base_confidence
    applied_rules = []

    # Gather folder information for rule evaluation
    folder_info = _analyze_folder_for_rules(folder_path)

    for rule in confidence_rules:
        try:
            rule_applied, adjustment = _evaluate_rule(rule, folder_info, tmdb_match)

            if rule_applied:
                old_confidence = adjusted_confidence
                adjusted_confidence = max(
                    0.0, min(1.0, adjusted_confidence + adjustment)
                )

                rule_description = (
                    f"{rule.get('name', 'Unnamed rule')}: {adjustment:+.2f}"
                )
                applied_rules.append(rule_description)

                logger.debug(
                    f"Applied rule '{rule.get('name', 'Unnamed')}': {old_confidence:.2f} -> {adjusted_confidence:.2f} ({adjustment:+.2f})"
                )

        except Exception as e:
            logger.warning(
                f"Error applying confidence rule '{rule.get('name', 'Unknown')}': {e}"
            )

    return adjusted_confidence, applied_rules


def _analyze_folder_for_rules(folder_path: Path) -> Dict[str, Any]:
    """Analyze folder to extract information for rule evaluation."""
    video_files, audio_files, subdirs, total_files = get_folder_info(folder_path)

    # Get file extensions
    file_extensions = set()
    file_sizes = []

    try:
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                file_extensions.add(file_path.suffix.lower().lstrip("."))
                try:
                    file_sizes.append(file_path.stat().st_size)
                except (OSError, PermissionError):
                    pass
    except (PermissionError, OSError):
        pass

    # Calculate metrics
    avg_file_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
    has_large_files = any(size > 500 * 1024 * 1024 for size in file_sizes)  # >500MB
    has_many_small_files = (
        len([s for s in file_sizes if s < 10 * 1024 * 1024]) > 10
    )  # >10 files <10MB

    # Check for season structure
    has_season_structure = False
    try:
        subdirectories = [
            item.name.lower() for item in folder_path.iterdir() if item.is_dir()
        ]
        season_dirs = [
            d
            for d in subdirectories
            if "season" in d or d.startswith("s") and d[1:].isdigit()
        ]
        has_season_structure = len(season_dirs) > 0
    except (PermissionError, OSError):
        pass

    return {
        "file_extensions": file_extensions,
        "video_files": video_files,
        "audio_files": audio_files,
        "subdirs": subdirs,
        "total_files": total_files,
        "avg_file_size": avg_file_size,
        "has_large_files": has_large_files,
        "single_large_video": video_files == 1 and has_large_files,
        "many_small_files": has_many_small_files,
        "has_season_structure": has_season_structure,
        "folder_name": folder_path.name.lower(),
    }


def _evaluate_rule(
    rule: Dict[str, Any], folder_info: Dict[str, Any], tmdb_match: bool
) -> Tuple[bool, float]:
    """
    Evaluate a single confidence rule.

    Args:
        rule: Rule dictionary with condition, value, and adjustment
        folder_info: Analyzed folder information
        tmdb_match: Whether TMDb found a match

    Returns:
        Tuple of (rule_applies, adjustment_value)
    """
    condition = rule.get("condition")
    expected_value = rule.get("value")
    adjustment = rule.get("adjustment", 0)

    if not condition or adjustment == 0:
        return False, 0

    # Evaluate different condition types
    if condition == "filetype":
        return expected_value in folder_info.get("file_extensions", set()), adjustment

    elif condition == "tmdb_match":
        return tmdb_match == expected_value, adjustment

    elif condition == "single_large_video":
        return (
            folder_info.get("single_large_video", False) == expected_value,
            adjustment,
        )

    elif condition == "many_small_files":
        return folder_info.get("many_small_files", False) == expected_value, adjustment

    elif condition == "has_season_structure":
        return (
            folder_info.get("has_season_structure", False) == expected_value,
            adjustment,
        )

    elif condition == "video_file_count":
        return (
            _compare_numeric(folder_info.get("video_files", 0), expected_value),
            adjustment,
        )

    elif condition == "audio_file_count":
        return (
            _compare_numeric(folder_info.get("audio_files", 0), expected_value),
            adjustment,
        )

    elif condition == "folder_name_contains":
        folder_name = folder_info.get("folder_name", "")
        if isinstance(expected_value, str):
            return expected_value.lower() in folder_name, adjustment
        elif isinstance(expected_value, list):
            return any(val.lower() in folder_name for val in expected_value), adjustment

    elif condition == "folder_name_matches":
        folder_name = folder_info.get("folder_name", "")
        if isinstance(expected_value, str):
            import re

            return bool(re.search(expected_value.lower(), folder_name)), adjustment

    # If no condition matched, return False
    return False, 0


def _compare_numeric(actual: int, expected: Any) -> bool:
    """Compare numeric values, supporting operators like '>5', '<=3', etc."""
    if isinstance(expected, int):
        return actual == expected

    if isinstance(expected, str):
        expected = expected.strip()

        # Parse operators
        if expected.startswith(">="):
            return actual >= int(expected[2:])
        elif expected.startswith("<="):
            return actual <= int(expected[2:])
        elif expected.startswith(">"):
            return actual > int(expected[1:])
        elif expected.startswith("<"):
            return actual < int(expected[1:])
        elif expected.startswith("="):
            return actual == int(expected[1:])
        else:
            try:
                return actual == int(expected)
            except ValueError:
                return False

    return False


def get_default_confidence_rules() -> List[Dict[str, Any]]:
    """Get default confidence rules."""
    return [
        {
            "name": "WAV files penalty",
            "condition": "filetype",
            "value": "wav",
            "adjustment": -0.3,
            "reason": "WAV files are often sound effects or samples, not music",
        },
        {
            "name": "TMDb match bonus",
            "condition": "tmdb_match",
            "value": True,
            "adjustment": 0.5,
            "reason": "TMDb match indicates legitimate media content",
        },
        {
            "name": "Single large video bonus",
            "condition": "single_large_video",
            "value": True,
            "adjustment": 0.2,
            "reason": "Single large video file likely indicates a movie",
        },
        {
            "name": "Many small files penalty",
            "condition": "many_small_files",
            "value": True,
            "adjustment": -0.2,
            "reason": "Many small files may indicate samples or non-media content",
        },
        {
            "name": "Season structure bonus",
            "condition": "has_season_structure",
            "value": True,
            "adjustment": 0.3,
            "reason": "Clear season structure indicates TV show",
        },
        {
            "name": "System folder penalty",
            "condition": "folder_name_contains",
            "value": ["system", "windows", "program", "appdata", "$recycle"],
            "adjustment": -0.8,
            "reason": "System folders should not be processed as media",
        },
        {
            "name": "Documentary bonus",
            "condition": "folder_name_contains",
            "value": ["documentary", "docu", "nature", "history"],
            "adjustment": 0.1,
            "reason": "Documentary keywords indicate legitimate media",
        },
    ]

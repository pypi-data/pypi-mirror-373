"""Media folder discovery and scanning."""

import logging
from pathlib import Path
from typing import Generator, List, Tuple

logger = logging.getLogger(__name__)


def is_media_folder(folder_path: Path) -> bool:
    """Check if a folder likely contains media files."""
    if not folder_path.is_dir():
        return False

    # Skip system and hidden folders
    if folder_path.name.startswith(".") or folder_path.name.startswith("$"):
        return False

    # Skip common non-media folders
    skip_folders = {
        "system volume information",
        "recycler",
        "$recycle.bin",
        "windows",
        "program files",
        "program files (x86)",
        "programdata",
        "users",
        "documents and settings",
        ".git",
        ".svn",
        "__pycache__",
    }

    if folder_path.name.lower() in skip_folders:
        return False

    # Check if folder contains any files (not just subdirectories)
    try:
        files = [f for f in folder_path.iterdir() if f.is_file()]
        return len(files) > 0
    except (PermissionError, OSError):
        logger.warning(f"Cannot access folder: {folder_path}")
        return False


def scan_for_media_folders(
    scan_dirs: List[str], max_depth: int = 3
) -> Generator[Path, None, None]:
    """
    Scan directories for potential media folders.

    Args:
        scan_dirs: List of directories to scan
        max_depth: Maximum directory depth to scan

    Yields:
        Path objects for potential media folders
    """
    for scan_dir in scan_dirs:
        scan_path = Path(scan_dir)

        if not scan_path.exists():
            logger.warning(f"Scan directory does not exist: {scan_dir}")
            continue

        logger.info(f"Scanning directory: {scan_dir}")

        try:
            yield from _scan_directory_recursive(scan_path, max_depth, 0)
        except (PermissionError, OSError) as e:
            logger.error(f"Error scanning {scan_dir}: {e}")


def _scan_directory_recursive(
    directory: Path, max_depth: int, current_depth: int
) -> Generator[Path, None, None]:
    """Recursively scan directory for media folders."""
    if current_depth >= max_depth:
        return

    try:
        for item in directory.iterdir():
            if item.is_dir() and is_media_folder(item):
                # Check if this looks like a complete media folder
                if _is_complete_media_folder(item):
                    yield item
                else:
                    # Continue scanning subdirectories
                    yield from _scan_directory_recursive(
                        item, max_depth, current_depth + 1
                    )
    except (PermissionError, OSError) as e:
        logger.warning(f"Cannot access directory {directory}: {e}")


def _is_complete_media_folder(folder_path: Path) -> bool:
    """
    Determine if a folder represents a complete media collection.

    This helps decide whether to treat a folder as a unit or scan deeper.
    """
    folder_name = folder_path.name.lower()

    # TV show season patterns
    if "season" in folder_name or any(
        f"season {i:02d}" in folder_name for i in range(1, 21)
    ):
        return True

    # Movie patterns (year in parentheses)
    if "(" in folder_name and ")" in folder_name:
        # Look for year pattern
        import re

        if re.search(r"\(19\d{2}\)|\(20\d{2}\)", folder_name):
            return True

    # Check for common media patterns
    media_patterns = [
        "complete",
        "collection",
        "series",
        "trilogy",
        "saga",
        "discography",
        "anthology",
        "box set",
        "boxset",
    ]

    if any(pattern in folder_name for pattern in media_patterns):
        return True

    # Check file structure
    try:
        subdirs = [item for item in folder_path.iterdir() if item.is_dir()]
        files = [item for item in folder_path.iterdir() if item.is_file()]

        # If there are video files directly in this folder, it's likely complete
        video_extensions = {
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
        }
        video_files = [f for f in files if f.suffix.lower() in video_extensions]

        if video_files:
            return True

        # If there are audio files and no subdirectories, likely complete
        audio_extensions = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a"}
        audio_files = [f for f in files if f.suffix.lower() in audio_extensions]

        if audio_files and len(subdirs) == 0:
            return True

        # If there are only a few subdirectories with clear names, scan deeper
        if len(subdirs) <= 3:
            return False

        return True

    except (PermissionError, OSError):
        return True  # Assume complete if we can't analyze


def get_folder_info(folder_path: Path) -> Tuple[int, int, int, int]:
    """
    Get basic information about folder contents.

    Returns:
        Tuple of (video_files, audio_files, subdirs, total_files)
    """
    try:
        items = list(folder_path.rglob("*"))
        files = [item for item in items if item.is_file()]
        subdirs = [item for item in items if item.is_dir()]

        video_extensions = {
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
        }
        audio_extensions = {".mp3", ".flac", ".wav", ".aac", ".ogg", ".wma", ".m4a"}

        video_files = len([f for f in files if f.suffix.lower() in video_extensions])
        audio_files = len([f for f in files if f.suffix.lower() in audio_extensions])

        return video_files, audio_files, len(subdirs), len(files)

    except (PermissionError, OSError):
        return 0, 0, 0, 0

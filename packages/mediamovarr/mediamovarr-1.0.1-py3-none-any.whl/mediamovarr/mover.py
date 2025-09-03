"""File moving operations with safety checks."""

import logging
import shutil
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class MoveResult(Enum):
    """Result of a move operation."""

    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"


def move_media(source_path: Path, dest_path: Path, force: bool = False) -> MoveResult:
    """
    Move media folder from source to destination with safety checks.

    Args:
        source_path: Source folder path
        dest_path: Destination folder path
        force: If True, overwrite existing files

    Returns:
        MoveResult indicating the outcome
    """
    logger.info(f"Moving {source_path.name} to {dest_path}")

    try:
        # Check if source exists
        if not source_path.exists():
            logger.error(f"Source path does not exist: {source_path}")
            return MoveResult.ERROR

        # Check if destination already exists
        if dest_path.exists():
            if not force:
                logger.warning(f"Destination already exists: {dest_path}")
                logger.info("Use --force to overwrite existing files")
                return MoveResult.SKIPPED
            else:
                logger.warning(f"Overwriting existing destination: {dest_path}")
                shutil.rmtree(dest_path)

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Perform the move
        shutil.move(str(source_path), str(dest_path))

        logger.info(f"Successfully moved to: {dest_path}")
        return MoveResult.SUCCESS

    except PermissionError as e:
        logger.error(f"Permission denied moving {source_path}: {e}")
        return MoveResult.ERROR
    except OSError as e:
        logger.error(f"OS error moving {source_path}: {e}")
        return MoveResult.ERROR
    except Exception as e:
        logger.error(f"Unexpected error moving {source_path}: {e}")
        return MoveResult.ERROR


def copy_media(source_path: Path, dest_path: Path, force: bool = False) -> MoveResult:
    """
    Copy media folder from source to destination (alternative to moving).

    Args:
        source_path: Source folder path
        dest_path: Destination folder path
        force: If True, overwrite existing files

    Returns:
        MoveResult indicating the outcome
    """
    logger.info(f"Copying {source_path.name} to {dest_path}")

    try:
        # Check if source exists
        if not source_path.exists():
            logger.error(f"Source path does not exist: {source_path}")
            return MoveResult.ERROR

        # Check if destination already exists
        if dest_path.exists():
            if not force:
                logger.warning(f"Destination already exists: {dest_path}")
                logger.info("Use --force to overwrite existing files")
                return MoveResult.SKIPPED
            else:
                logger.warning(f"Overwriting existing destination: {dest_path}")
                shutil.rmtree(dest_path)

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Perform the copy
        if source_path.is_dir():
            shutil.copytree(str(source_path), str(dest_path))
        else:
            shutil.copy2(str(source_path), str(dest_path))

        logger.info(f"Successfully copied to: {dest_path}")
        return MoveResult.SUCCESS

    except PermissionError as e:
        logger.error(f"Permission denied copying {source_path}: {e}")
        return MoveResult.ERROR
    except OSError as e:
        logger.error(f"OS error copying {source_path}: {e}")
        return MoveResult.ERROR
    except Exception as e:
        logger.error(f"Unexpected error copying {source_path}: {e}")
        return MoveResult.ERROR


def safe_filename(filename: str) -> str:
    """
    Make filename safe for filesystem by removing/replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    import re

    # Replace invalid characters with underscores
    # Windows invalid characters: < > : " | ? * \ /
    # Also remove control characters
    safe_name = re.sub(r'[<>:"|?*\\/\x00-\x1f]', "_", filename)

    # Remove leading/trailing dots and spaces (Windows doesn't like these)
    safe_name = safe_name.strip(". ")

    # Ensure not empty
    if not safe_name:
        safe_name = "unnamed"

    # Truncate if too long (most filesystems have 255 char limit)
    if len(safe_name) > 250:
        safe_name = safe_name[:250]

    return safe_name


def get_available_path(path: Path) -> Path:
    """
    Get an available path by appending numbers if the path already exists.

    Args:
        path: Desired path

    Returns:
        Available path (may be the same as input if not taken)
    """
    if not path.exists():
        return path

    base_path = path.parent
    stem = path.stem
    suffix = path.suffix

    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = base_path / new_name

        if not new_path.exists():
            return new_path

        counter += 1

        # Prevent infinite loop
        if counter > 1000:
            raise ValueError(f"Could not find available path for {path}")


def validate_move(source_path: Path, dest_path: Path) -> Optional[str]:
    """
    Validate a move operation before executing it.

    Args:
        source_path: Source path
        dest_path: Destination path

    Returns:
        Error message if validation fails, None if OK
    """
    # Check if source exists
    if not source_path.exists():
        return f"Source does not exist: {source_path}"

    # Check if we have read permission on source
    if not source_path.is_dir() and not source_path.is_file():
        return f"Source is neither file nor directory: {source_path}"

    # Check if destination is inside source (would cause recursion)
    try:
        dest_path.resolve().relative_to(source_path.resolve())
        return f"Destination is inside source directory: {dest_path}"
    except ValueError:
        # This is good - dest is not inside source
        pass

    # Check if we can create the destination directory
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        return f"Cannot create destination directory: {e}"

    return None

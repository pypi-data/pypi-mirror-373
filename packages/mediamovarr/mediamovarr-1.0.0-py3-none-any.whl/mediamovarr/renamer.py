"""File and folder renaming according to Plex guidelines."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .classify import MediaType

logger = logging.getLogger(__name__)


def get_renamed_path(
    folder_path: Path, media_type: str, config: Dict[str, Any]
) -> Optional[Path]:
    """
    Generate the destination path for a media folder based on Plex guidelines.

    Args:
        folder_path: Source folder path
        media_type: Detected media type
        config: Configuration dictionary

    Returns:
        Destination path or None if renaming fails
    """
    dest_dir = Path(config["dest_dir"])

    try:
        if media_type == MediaType.TV:
            return _rename_tv_show(folder_path, dest_dir, config)
        elif media_type == MediaType.MOVIE:
            return _rename_movie(folder_path, dest_dir, config)
        elif media_type == MediaType.MUSIC:
            return _rename_music(folder_path, dest_dir, config)
        elif media_type == MediaType.AUDIOBOOK:
            return _rename_audiobook(folder_path, dest_dir, config)
        else:
            logger.warning(f"Unknown media type for renaming: {media_type}")
            return None

    except Exception as e:
        logger.error(f"Error renaming {folder_path}: {e}")
        return None


def _rename_tv_show(folder_path: Path, dest_dir: Path, config: Dict[str, Any]) -> Path:
    """Rename TV show according to Plex guidelines."""
    folder_name = folder_path.name

    # Extract show title and season
    title, season = _parse_tv_show_name(folder_name)

    if not title:
        # Fallback to original name
        title = _clean_title(folder_name)

    # Create destination path: TV Shows/Show Name/Season XX/
    tv_dir = dest_dir / "TV Shows"
    show_dir = tv_dir / title

    if season is not None:
        season_dir = show_dir / f"Season {season:02d}"
        return season_dir
    else:
        return show_dir


def _rename_movie(folder_path: Path, dest_dir: Path, config: Dict[str, Any]) -> Path:
    """Rename movie according to Plex guidelines."""
    folder_name = folder_path.name

    # Extract movie title and year
    title, year = _parse_movie_name(folder_name)

    if not title:
        title = _clean_title(folder_name)

    # Create destination path: Movies/Title (Year)/
    movies_dir = dest_dir / "Movies"

    if year:
        movie_dir = movies_dir / f"{title} ({year})"
    else:
        movie_dir = movies_dir / title

    return movie_dir


def _rename_music(folder_path: Path, dest_dir: Path, config: Dict[str, Any]) -> Path:
    """Rename music according to common organization."""
    folder_name = folder_path.name

    # Try to extract artist and album
    artist, album = _parse_music_name(folder_name)

    if not artist:
        artist = "Unknown Artist"
    if not album:
        album = _clean_title(folder_name)

    # Create destination path: Music/Artist/Album/
    music_dir = dest_dir / "Music"
    artist_dir = music_dir / artist
    album_dir = artist_dir / album

    return album_dir


def _rename_audiobook(
    folder_path: Path, dest_dir: Path, config: Dict[str, Any]
) -> Path:
    """Rename audiobook according to common organization."""
    folder_name = folder_path.name

    # Try to extract author and title
    author, title = _parse_audiobook_name(folder_name)

    if not author:
        author = "Unknown Author"
    if not title:
        title = _clean_title(folder_name)

    # Create destination path: Audiobooks/Author/Title/
    audiobook_dir = dest_dir / "Audiobooks"
    author_dir = audiobook_dir / author
    title_dir = author_dir / title

    return title_dir


def _parse_tv_show_name(folder_name: str) -> Tuple[Optional[str], Optional[int]]:
    """Parse TV show name to extract title and season number."""
    folder_name = folder_name.strip()

    # Pattern 1: Show Name Season X
    pattern1 = re.search(r"^(.+?)\s+season\s+(\d+)", folder_name, re.IGNORECASE)
    if pattern1:
        title = pattern1.group(1).strip()
        season = int(pattern1.group(2))
        return _clean_title(title), season

    # Pattern 2: Show Name SX
    pattern2 = re.search(r"^(.+?)\s+s(\d+)", folder_name, re.IGNORECASE)
    if pattern2:
        title = pattern2.group(1).strip()
        season = int(pattern2.group(2))
        return _clean_title(title), season

    # Pattern 3: Show Name (Year) Season X
    pattern3 = re.search(
        r"^(.+?)\s*\(\d{4}\)\s*season\s+(\d+)", folder_name, re.IGNORECASE
    )
    if pattern3:
        title = pattern3.group(1).strip()
        season = int(pattern3.group(2))
        return _clean_title(title), season

    # Pattern 4: Just show name (no season info)
    # Remove common junk at the end
    clean_name = re.sub(r"\s*[\[\(].*?[\]\)]", "", folder_name)
    clean_name = re.sub(
        r"\s*(complete|series|collection).*$", "", clean_name, flags=re.IGNORECASE
    )

    return _clean_title(clean_name), None


def _parse_movie_name(folder_name: str) -> Tuple[Optional[str], Optional[int]]:
    """Parse movie name to extract title and year."""
    folder_name = folder_name.strip()

    # Pattern 1: Title (Year)
    pattern1 = re.search(r"^(.+?)\s*\((\d{4})\)", folder_name)
    if pattern1:
        title = pattern1.group(1).strip()
        year = int(pattern1.group(2))
        return _clean_title(title), year

    # Pattern 2: Title Year (without parentheses)
    pattern2 = re.search(r"^(.+?)\s+(\d{4})(?:\s|$)", folder_name)
    if pattern2:
        title = pattern2.group(1).strip()
        year = int(pattern2.group(2))
        return _clean_title(title), year

    # Pattern 3: Just title (no year)
    clean_name = re.sub(r"\s*[\[\(].*?[\]\)]", "", folder_name)
    clean_name = re.sub(
        r"\s*(bluray|dvdrip|webrip|hdtv|1080p|720p|4k).*$",
        "",
        clean_name,
        flags=re.IGNORECASE,
    )

    return _clean_title(clean_name), None


def _parse_music_name(folder_name: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse music folder name to extract artist and album."""
    folder_name = folder_name.strip()

    # Pattern 1: Artist - Album
    pattern1 = re.match(r"^(.+?)\s*-\s*(.+?)$", folder_name)
    if pattern1:
        artist = pattern1.group(1).strip()
        album = pattern1.group(2).strip()
        return _clean_title(artist), _clean_title(album)

    # Pattern 2: Artist_Album or Artist.Album
    pattern2 = re.match(r"^(.+?)[._](.+?)$", folder_name)
    if pattern2:
        artist = pattern2.group(1).strip()
        album = pattern2.group(2).strip()
        return _clean_title(artist), _clean_title(album)

    # Pattern 3: Just album name
    return None, _clean_title(folder_name)


def _parse_audiobook_name(folder_name: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse audiobook folder name to extract author and title."""
    folder_name = folder_name.strip()

    # Pattern 1: Author - Title
    pattern1 = re.match(r"^(.+?)\s*-\s*(.+?)$", folder_name)
    if pattern1:
        author = pattern1.group(1).strip()
        title = pattern1.group(2).strip()
        return _clean_title(author), _clean_title(title)

    # Pattern 2: Title by Author
    pattern2 = re.search(r"^(.+?)\s+by\s+(.+?)$", folder_name, re.IGNORECASE)
    if pattern2:
        title = pattern2.group(1).strip()
        author = pattern2.group(2).strip()
        return _clean_title(author), _clean_title(title)

    # Pattern 3: Just title
    return None, _clean_title(folder_name)


def _clean_title(title: str) -> str:
    """Clean up title by removing common junk."""
    if not title:
        return "Unknown"

    # Remove bracketed content
    title = re.sub(r"\s*[\[\(].*?[\]\)]", "", title)

    # Remove common release info
    junk_patterns = [
        r"\b(bluray|blu-ray|dvdrip|webrip|hdtv|pdtv|hdcam|cam|ts|tc)\b",
        r"\b(1080p|720p|480p|4k|uhd|2160p)\b",
        r"\b(x264|x265|h264|h265|hevc|xvid|divx)\b",
        r"\b(aac|ac3|dts|mp3|flac)\b",
        r"\b(proper|repack|internal|limited|extended|unrated|directors|cut)\b",
        r"\b(complete|collection|series|season|s\d+)\b",
        r"\b(www\.\w+\.\w+)\b",  # Remove website names
    ]

    for pattern in junk_patterns:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)

    # Remove multiple spaces and clean up
    title = re.sub(r"\s+", " ", title).strip()

    # Remove leading/trailing dots, dashes, underscores
    title = re.sub(r"^[\.\-_\s]+|[\.\-_\s]+$", "", title)

    # Capitalize properly
    title = title.title()

    return title or "Unknown"

"""Media type classification logic."""

import logging
import re
from pathlib import Path
from typing import Optional, Tuple

from .discovery import get_folder_info

logger = logging.getLogger(__name__)


class MediaType:
    TV = "tv"
    MOVIE = "movie"
    MUSIC = "music"
    AUDIOBOOK = "audiobook"
    UNKNOWN = "unknown"


def classify_media(folder_path: Path, tmdb_client=None) -> Tuple[str, float, bool]:
    """
    Classify media folder and return type with confidence score.

    Args:
        folder_path: Path to the media folder
        tmdb_client: Optional TMDb client for enhanced classification

    Returns:
        Tuple of (media_type, confidence_score, tmdb_match_found)
    """
    folder_name = folder_path.name.lower()
    video_files, audio_files, subdirs, total_files = get_folder_info(folder_path)

    logger.debug(
        f"Classifying {folder_path.name}: {video_files} video, {audio_files} audio, {subdirs} subdirs"
    )

    # Get base confidence scores from pattern matching
    tv_confidence = _detect_tv_show(
        folder_path, folder_name, video_files, audio_files, subdirs
    )
    movie_confidence = _detect_movie(
        folder_path, folder_name, video_files, audio_files, subdirs
    )
    music_confidence = _detect_music(
        folder_path, folder_name, video_files, audio_files, subdirs
    )
    audiobook_confidence = _detect_audiobook(
        folder_path, folder_name, video_files, audio_files, subdirs
    )

    # Apply TMDb smart validation if available and video content detected
    tmdb_match_found = False
    if tmdb_client and (video_files > 0):
        tv_confidence, movie_confidence, tmdb_match_found = _apply_tmdb_validation(
            folder_path, tmdb_client, tv_confidence, movie_confidence
        )

    # Check for clear winners above threshold
    if tv_confidence > 0.7:
        return MediaType.TV, tv_confidence, tmdb_match_found
    if movie_confidence > 0.7:
        return MediaType.MOVIE, movie_confidence, tmdb_match_found
    if music_confidence > 0.7:
        return MediaType.MUSIC, music_confidence, tmdb_match_found
    if audiobook_confidence > 0.7:
        return MediaType.AUDIOBOOK, audiobook_confidence, tmdb_match_found

    # Return highest confidence classification
    classifications = [
        (MediaType.TV, tv_confidence),
        (MediaType.MOVIE, movie_confidence),
        (MediaType.MUSIC, music_confidence),
        (MediaType.AUDIOBOOK, audiobook_confidence),
    ]

    best_type, best_confidence = max(classifications, key=lambda x: x[1])

    if best_confidence < 0.3:
        return MediaType.UNKNOWN, best_confidence, tmdb_match_found

    return best_type, best_confidence, tmdb_match_found


def _apply_tmdb_validation(
    folder_path: Path, tmdb_client, tv_confidence: float, movie_confidence: float
) -> Tuple[float, float, bool]:
    """
    Apply TMDb-based validation to adjust TV/Movie confidence scores.

    Logic:
    - If TMDb finds TV match but no movie match → Strong boost to TV confidence
    - If TMDb finds movie match but no TV match → Strong boost to movie confidence
    - If both or neither found → Smaller adjustments based on match quality
    """
    title = _extract_title_from_folder(folder_path.name)
    year = _extract_year_from_folder(folder_path.name)

    logger.debug(f"TMDb validation for: '{title}' (year: {year})")

    # Search both TV and movie databases
    tv_match = tmdb_client.search_tv_show(title, year)
    movie_match = tmdb_client.search_movie(title, year)

    tmdb_match_found = bool(tv_match or movie_match)

    # Strong validation: One type matches, the other doesn't
    if tv_match and not movie_match:
        logger.info("TMDb: TV show found, no movie match → Strong TV confidence boost")
        tv_confidence = min(tv_confidence + 0.7, 1.0)  # Strong boost
        movie_confidence = max(movie_confidence - 0.3, 0.0)  # Penalty to movie

    elif movie_match and not tv_match:
        logger.info(
            "TMDb: Movie found, no TV show match → Strong movie confidence boost"
        )
        movie_confidence = min(movie_confidence + 0.7, 1.0)  # Strong boost
        tv_confidence = max(tv_confidence - 0.3, 0.0)  # Penalty to TV

    elif tv_match and movie_match:
        # Both found - use match quality and original confidence to decide
        logger.info("TMDb: Both TV and movie matches found - using match quality")

        # Check which has better match score (TMDb popularity/vote_average)
        tv_score = tv_match.get("popularity", 0) + tv_match.get("vote_average", 0) * 10
        movie_score = (
            movie_match.get("popularity", 0) + movie_match.get("vote_average", 0) * 10
        )

        if tv_score > movie_score:
            tv_confidence = min(tv_confidence + 0.3, 1.0)
            movie_confidence = max(movie_confidence - 0.1, 0.0)
        elif movie_score > tv_score:
            movie_confidence = min(movie_confidence + 0.3, 1.0)
            tv_confidence = max(tv_confidence - 0.1, 0.0)
        # If scores are similar, leave confidence as-is

    else:
        # Neither found - small penalty to both (might be misnamed or very obscure)
        logger.debug(f"TMDb: No matches found for '{title}'")
        tv_confidence = max(tv_confidence - 0.1, 0.0)
        movie_confidence = max(movie_confidence - 0.1, 0.0)

    return tv_confidence, movie_confidence, tmdb_match_found


def _extract_title_from_folder(folder_name: str) -> str:
    """Extract clean title from folder name for TMDb search."""
    # Remove common patterns that interfere with TMDb searches
    title = folder_name

    # Remove quality indicators
    title = re.sub(
        r"\b(1080p|720p|480p|4k|uhd|hd|sd)\b", "", title, flags=re.IGNORECASE
    )

    # Remove source indicators
    title = re.sub(
        r"\b(bluray|blu-ray|dvdrip|webrip|hdtv|web-dl|brrip)\b",
        "",
        title,
        flags=re.IGNORECASE,
    )

    # Remove encoding info
    title = re.sub(
        r"\b(x264|x265|h264|h265|xvid|divx)\b", "", title, flags=re.IGNORECASE
    )

    # Remove group tags (usually at the end)
    title = re.sub(r"-[A-Z0-9]+$", "", title, flags=re.IGNORECASE)

    # Remove episode info for TV shows to get series title
    title = re.sub(r"\bs\d+e\d+.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\b\d+x\d+.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bseason\s*\d+.*$", "", title, flags=re.IGNORECASE)

    # Replace dots/underscores with spaces
    title = re.sub(r"[._]", " ", title)

    # Clean up extra whitespace
    title = " ".join(title.split())

    return title.strip()


def _extract_year_from_folder(folder_name: str) -> Optional[int]:
    """Extract year from folder name."""
    # Look for year in parentheses first (most reliable)
    year_match = re.search(r"\((\d{4})\)", folder_name)
    if year_match:
        return int(year_match.group(1))

    # Look for standalone 4-digit year
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", folder_name)
    if year_match:
        return int(year_match.group(1))

    return None


def _detect_tv_show(
    folder_path: Path,
    folder_name: str,
    video_files: int,
    audio_files: int,
    subdirs: int,
) -> float:
    """Detect TV show with confidence score."""
    confidence = 0.0

    # Check for episode patterns first (highest priority for TV shows)
    episode_patterns = [
        r"s\d+e\d+",  # S01E01 format
        r"season\s*\d+.*episode\s*\d+",
        r"\d+x\d+",  # 1x01 format
        r"episode\s*\d+",
    ]

    for pattern in episode_patterns:
        if re.search(pattern, folder_name, re.IGNORECASE):
            confidence += 0.8  # Strong indicator for TV shows
            break

    # Check for season indicators
    season_patterns = [
        r"season\s*\d+",
        r"s\d+",
        r"series\s*\d+",
        r"season\s*0?\d",
        r"complete\s*series",
    ]

    for pattern in season_patterns:
        if re.search(pattern, folder_name, re.IGNORECASE):
            confidence += 0.4
            break

    # Check subdirectory structure for seasons
    try:
        subdirectories = [
            item.name.lower() for item in folder_path.iterdir() if item.is_dir()
        ]
        season_subdirs = sum(
            1
            for subdir in subdirectories
            if "season" in subdir or re.match(r"s\d+", subdir)
        )

        if season_subdirs > 0:
            confidence += 0.5

        # Check for episode files in subdirectories
        episode_files = 0
        for subdir in folder_path.iterdir():
            if subdir.is_dir():
                files = [f.name.lower() for f in subdir.iterdir() if f.is_file()]
                for file_name in files:
                    if any(
                        re.search(pattern, file_name) for pattern in episode_patterns
                    ):
                        episode_files += 1

        if episode_files > 2:
            confidence += 0.3

    except (PermissionError, OSError):
        pass

    # Penalize if mostly audio files
    if audio_files > video_files * 2:
        confidence *= 0.5

    return min(confidence, 1.0)


def _detect_movie(
    folder_path: Path,
    folder_name: str,
    video_files: int,
    audio_files: int,
    subdirs: int,
) -> float:
    """Detect movie with confidence score."""
    confidence = 0.0

    # Strong penalty if clear TV show indicators are present
    tv_indicators = [r"s\d+e\d+", r"\d+x\d+", r"season\s*\d+", r"episode\s*\d+"]
    for pattern in tv_indicators:
        if re.search(pattern, folder_name, re.IGNORECASE):
            confidence -= 0.6  # Strong penalty for TV show patterns
            break

    # Check for year in parentheses
    year_pattern = r"\(19\d{2}\)|\(20\d{2}\)"
    if re.search(year_pattern, folder_name):
        confidence += 0.6

    # Check for movie-specific keywords
    movie_keywords = [
        "movie",
        "film",
        "cinema",
        "bluray",
        "blu-ray",
        "dvdrip",
        "webrip",
        "hdtv",
        "1080p",
        "720p",
        "4k",
        "uhd",
        "directors cut",
        "extended",
        "unrated",
        "theatrical",
    ]

    keyword_matches = sum(1 for keyword in movie_keywords if keyword in folder_name)
    confidence += min(keyword_matches * 0.1, 0.3)  # Reduced from 0.2 per match to 0.1

    # Single large video file is typical for movies
    if video_files == 1 and audio_files <= 2:
        confidence += 0.4
    elif video_files <= 3 and audio_files <= 5:  # Including alternate versions
        confidence += 0.2

    # Few subdirectories suggests single movie
    if subdirs <= 2:
        confidence += 0.2

    # Check file sizes (movies typically have larger files)
    try:
        video_files_list = []
        for item in folder_path.rglob("*"):
            if item.is_file() and item.suffix.lower() in {
                ".mp4",
                ".mkv",
                ".avi",
                ".mov",
                ".wmv",
            }:
                video_files_list.append(item)

        if video_files_list:
            # Check if main video file is large (> 500MB suggests movie)
            largest_file = max(
                video_files_list, key=lambda f: f.stat().st_size if f.exists() else 0
            )
            if largest_file.stat().st_size > 500 * 1024 * 1024:  # 500MB
                confidence += 0.2

    except (PermissionError, OSError):
        pass

    # Penalize if many audio files (suggests music/audiobook)
    if audio_files > 10:
        confidence *= 0.3

    return min(confidence, 1.0)


def _detect_music(
    folder_path: Path,
    folder_name: str,
    video_files: int,
    audio_files: int,
    subdirs: int,
) -> float:
    """Detect music with confidence score."""
    confidence = 0.0

    # High ratio of audio to video files
    if audio_files > 0 and video_files == 0:
        confidence += 0.5
    elif audio_files > video_files * 3:
        confidence += 0.3

    # Check for music-specific keywords
    music_keywords = [
        "album",
        "discography",
        "soundtrack",
        "ost",
        "single",
        "ep",
        "compilation",
        "greatest hits",
        "best of",
        "live",
        "concert",
        "flac",
        "mp3",
        "320kbps",
        "lossless",
    ]

    keyword_matches = sum(1 for keyword in music_keywords if keyword in folder_name)
    confidence += min(keyword_matches * 0.2, 0.4)

    # Check for artist/album structure
    try:
        # Look for track numbering in files
        audio_files_list = []
        for item in folder_path.rglob("*"):
            if item.is_file() and item.suffix.lower() in {
                ".mp3",
                ".flac",
                ".wav",
                ".aac",
                ".ogg",
                ".m4a",
            }:
                audio_files_list.append(item.name.lower())

        # Check for track numbering patterns
        numbered_tracks = sum(
            1 for name in audio_files_list if re.match(r"^\d+[\s\-\.]", name)
        )
        if numbered_tracks >= 3:
            confidence += 0.3

        # Check for common music file organization
        if len(audio_files_list) >= 3 and subdirs <= 3:
            confidence += 0.2

    except (PermissionError, OSError):
        pass

    # Year pattern in music (often just year, not in parentheses)
    if re.search(r"\b19\d{2}\b|\b20\d{2}\b", folder_name) and not re.search(
        r"\(19\d{2}\)|\(20\d{2}\)", folder_name
    ):
        confidence += 0.1

    return min(confidence, 1.0)


def _detect_audiobook(
    folder_path: Path,
    folder_name: str,
    video_files: int,
    audio_files: int,
    subdirs: int,
) -> float:
    """Detect audiobook with confidence score."""
    confidence = 0.0

    # Must have audio files, minimal/no video
    if audio_files < 3 or video_files > 1:
        return 0.0

    # Check for audiobook-specific keywords
    audiobook_keywords = [
        "audiobook",
        "audio book",
        "unabridged",
        "abridged",
        "narrated",
        "narrator",
        "chapter",
        "part",
        "cd1",
        "cd2",
        "disc",
        "book",
    ]

    keyword_matches = sum(1 for keyword in audiobook_keywords if keyword in folder_name)
    confidence += min(keyword_matches * 0.3, 0.6)

    # Check for chapter/part numbering
    try:
        audio_files_list = []
        for item in folder_path.rglob("*"):
            if item.is_file() and item.suffix.lower() in {
                ".mp3",
                ".flac",
                ".wav",
                ".aac",
                ".ogg",
                ".m4a",
            }:
                audio_files_list.append(item.name.lower())

        # Look for chapter patterns
        chapter_patterns = [
            r"chapter\s*\d+",
            r"ch\s*\d+",
            r"part\s*\d+",
            r"cd\s*\d+",
            r"disc\s*\d+",
            r"\d+\s*of\s*\d+",
        ]

        chapter_files = 0
        for file_name in audio_files_list:
            if any(re.search(pattern, file_name) for pattern in chapter_patterns):
                chapter_files += 1

        if chapter_files >= 3:
            confidence += 0.4

        # Long audio files suggest audiobook chapters
        if (
            len(audio_files_list) >= 5 and len(audio_files_list) <= 50
        ):  # Typical chapter count
            confidence += 0.2

    except (PermissionError, OSError):
        pass

    # Author name patterns (common in audiobook folder names)
    if re.search(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", folder_name):
        confidence += 0.1

    return min(confidence, 1.0)

"""TMDb API client for movie and TV show metadata lookup."""

import logging
import time
from typing import Any, Dict, Optional

import requests

from .database import get_database

logger = logging.getLogger(__name__)


class TMDbClient:
    """Client for The Movie Database (TMDb) API."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(
        self,
        api_key: str = "",
        read_access_token: str = "",
        db_path: str = "mediamovarr.db",
    ):
        """
        Initialize TMDb client.

        Args:
            api_key: TMDb API key
            read_access_token: TMDb read access token (preferred)
            db_path: Path to SQLite database for caching
        """
        self.api_key = api_key
        self.read_access_token = read_access_token
        self.db = get_database(db_path)
        self.last_request_time = 0.0
        self.rate_limit_delay = 0.25  # 4 requests per second max

        if not api_key and not read_access_token:
            logger.warning("No TMDb credentials provided - TMDb features disabled")

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make rate-limited request to TMDb API."""
        if not self.api_key and not self.read_access_token:
            return None

        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)

        url = f"{self.BASE_URL}/{endpoint}"

        # Set up headers and params
        headers = {}
        if self.read_access_token:
            headers["Authorization"] = f"Bearer {self.read_access_token}"
        elif self.api_key:
            params["api_key"] = self.api_key

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            self.last_request_time = time.time()

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("TMDb rate limit exceeded, backing off")
                time.sleep(2)
                return None
            else:
                logger.warning(
                    f"TMDb API error {response.status_code}: {response.text}"
                )
                return None

        except requests.RequestException as e:
            logger.error(f"TMDb request failed: {e}")
            return None

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """
        Search for a movie by title and year.

        Args:
            title: Movie title
            year: Release year (optional)

        Returns:
            Movie data or None if not found
        """
        cache_key = f"movie:{title}:{year}"

        # Check database cache first
        cached_result = self.db.get_tmdb_cache(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for movie: {title}")
            return cached_result

        # Make API request
        params = {"query": title}
        if year:
            params["year"] = str(year)

        result = self._make_request("search/movie", params)

        if result and result.get("results"):
            # Return the first result
            movie = result["results"][0]
            self.db.set_tmdb_cache(cache_key, "movie", title, year, movie)
            logger.info(
                f"Found movie: {movie.get('title')} ({movie.get('release_date', 'Unknown year')[:4]})"
            )
            return movie

        logger.info(f"Movie not found: {title}")
        self.db.set_tmdb_cache(cache_key, "movie", title, year, None)
        return None

    def search_tv_show(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """
        Search for a TV show by title and year.

        Args:
            title: TV show title
            year: First air year (optional)

        Returns:
            TV show data or None if not found
        """
        cache_key = f"tv:{title}:{year}"

        # Check database cache first
        cached_result = self.db.get_tmdb_cache(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for TV show: {title}")
            return cached_result

        # Make API request
        params = {"query": title}
        if year:
            params["first_air_date_year"] = str(year)

        result = self._make_request("search/tv", params)

        if result and result.get("results"):
            # Return the first result
            show = result["results"][0]
            self.db.set_tmdb_cache(cache_key, "tv", title, year, show)
            logger.info(
                f"Found TV show: {show.get('name')} ({show.get('first_air_date', 'Unknown year')[:4]})"
            )
            return show

        logger.info(f"TV show not found: {title}")
        self.db.set_tmdb_cache(cache_key, "tv", title, year, None)
        return None

    def get_tv_season(self, tv_id: int, season_number: int) -> Optional[Dict]:
        """
        Get detailed information about a TV season.

        Args:
            tv_id: TMDb TV show ID
            season_number: Season number

        Returns:
            Season data or None if not found
        """
        cache_key = f"season:{tv_id}:{season_number}"

        # Check database cache first
        cached_result = self.db.get_tmdb_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # Make API request
        result = self._make_request(f"tv/{tv_id}/season/{season_number}", {})

        if result:
            self.db.set_tmdb_cache(
                cache_key, "season", f"TV {tv_id}", season_number, result
            )
            return result

        return None

    def normalize_movie_title(
        self, title: str, year: Optional[int] = None
    ) -> tuple[str, Optional[int]]:
        """
        Normalize movie title using TMDb data.

        Args:
            title: Original title
            year: Original year

        Returns:
            Tuple of (normalized_title, normalized_year)
        """
        movie = self.search_movie(title, year)

        if movie:
            tmdb_title = movie.get("title", title)
            tmdb_year = None

            release_date = movie.get("release_date")
            if release_date:
                try:
                    tmdb_year = int(release_date[:4])
                except (ValueError, TypeError):
                    tmdb_year = year

            return tmdb_title, tmdb_year or year

        return title, year

    def normalize_tv_title(
        self, title: str, year: Optional[int] = None
    ) -> tuple[str, Optional[int]]:
        """
        Normalize TV show title using TMDb data.

        Args:
            title: Original title
            year: Original year

        Returns:
            Tuple of (normalized_title, normalized_year)
        """
        show = self.search_tv_show(title, year)

        if show:
            tmdb_title = show.get("name", title)
            tmdb_year = None

            first_air_date = show.get("first_air_date")
            if first_air_date:
                try:
                    tmdb_year = int(first_air_date[:4])
                except (ValueError, TypeError):
                    tmdb_year = year

            return tmdb_title, tmdb_year or year

        return title, year


def create_tmdb_client(
    config: Dict[str, Any], db_path: str = "mediamovarr.db"
) -> Optional[TMDbClient]:
    """
    Create TMDb client from configuration.

    Args:
        config: Configuration dictionary
        db_path: Path to SQLite database

    Returns:
        TMDbClient instance or None if TMDb is disabled
    """
    if not config.get("tmdb_enabled", False):
        return None

    api_key = config.get("tmdb_api_key", "")
    read_access_token = config.get("tmdb_read_access_token", "")

    if not api_key and not read_access_token:
        logger.warning("TMDb enabled but no credentials provided")
        return None

    return TMDbClient(
        api_key=api_key, read_access_token=read_access_token, db_path=db_path
    )

"""Tests for SQLite database integration with MediaMovarr."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mediamovarr.database import get_database


class TestDatabaseIntegration:
    """Test SQLite database functionality."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file path."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name
        yield db_path
        # Cleanup - ensure file is not locked
        try:
            Path(db_path).unlink(missing_ok=True)
        except PermissionError:
            # If file is locked, just pass - it will be cleaned up later
            pass

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for TMDb client."""
        return {"tmdb_enabled": True, "tmdb_api_key": "test_key_123"}

    def test_database_initialization(self, temp_db_path):
        """Test database initialization."""
        db = get_database(temp_db_path)
        assert db is not None, "Database initialization failed"

        # Test that tables are created
        # We can verify this by checking if basic operations work
        result = db.get_tmdb_cache("nonexistent")
        assert (
            result is None
        ), "Database should return None for non-existent cache entry"

        db.close()

    def test_tmdb_cache_operations(self, temp_db_path):
        """Test TMDb cache operations."""
        db = get_database(temp_db_path)

        # Test cache miss
        cache_key1 = "movie:Inception:2010"
        cache_key2 = "tv:Arrow:2012"

        result1 = db.get_tmdb_cache(cache_key1)
        result2 = db.get_tmdb_cache(cache_key2)
        assert result1 is None
        assert result2 is None

        # Test cache set and get
        movie_data = {"title": "Inception", "release_date": "2010-07-16", "id": 27205}
        tv_data = {"name": "Arrow", "first_air_date": "2012-10-10", "id": 1412}

        db.set_tmdb_cache(cache_key1, "movie", "Inception", 2010, movie_data)
        db.set_tmdb_cache(cache_key2, "tv", "Arrow", 2012, tv_data)

        cached_movie = db.get_tmdb_cache(cache_key1)
        cached_tv = db.get_tmdb_cache(cache_key2)

        assert cached_movie == movie_data
        assert cached_tv == tv_data

        # Test cache miss (not found)
        db.set_tmdb_cache("movie:NonExistent:2025", "movie", "NonExistent", 2025, None)
        cached_none = db.get_tmdb_cache("movie:NonExistent:2025")
        assert cached_none is None

        db.close()

    def test_user_exclusions(self, temp_db_path):
        """Test user exclusions functionality."""
        db = get_database(temp_db_path)

        test_path1 = "/downloads/Sample.Folder"
        test_path2 = "/downloads/Another.Folder"

        # Test non-excluded folders
        assert not db.is_excluded(test_path1)
        assert not db.is_excluded(test_path2)

        # Add exclusions
        db.add_exclusion(test_path1, "Sample.Folder", "movie", 0.85, "Test exclusion")
        db.add_exclusion(test_path2, "Another.Folder", "tv", 0.92)

        # Test excluded folders
        assert db.is_excluded(test_path1)
        assert db.is_excluded(test_path2)

        # Get exclusions list
        exclusions = db.get_exclusions()
        assert len(exclusions) == 2

        # Verify exclusion details
        exclusion_paths = [ex["folder_path"] for ex in exclusions]
        assert len(exclusion_paths) == 2
        assert test_path1 in exclusion_paths
        assert test_path2 in exclusion_paths

        # Verify the first exclusion details (order may vary)
        first_exclusion = exclusions[0]
        assert first_exclusion["folder_path"] in [test_path1, test_path2]
        assert first_exclusion["folder_name"] in ["Sample.Folder", "Another.Folder"]

        # Remove exclusion
        db.remove_exclusion(test_path1)
        assert not db.is_excluded(test_path1)
        assert db.is_excluded(test_path2)

        # Verify updated exclusions list
        exclusions = db.get_exclusions()
        assert len(exclusions) == 1
        assert exclusions[0]["folder_path"] == test_path2

        db.close()

    def test_processing_history(self, temp_db_path):
        """Test processing history functionality."""
        db = get_database(temp_db_path)

        # Add processing records
        db.add_processing_record(
            "/downloads/Movie.2020",
            "Movie.2020",
            "movie",
            0.95,
            "/media/movies/Movie (2020)",
            "moved",
            {"tmdb_match": True},
        )

        db.add_processing_record(
            "/downloads/Show.S01E01",
            "Show.S01E01",
            "tv",
            0.45,
            action="skipped",
            details={"reason": "low_confidence"},
        )

        db.add_processing_record(
            "/downloads/Unknown.Stuff",
            "Unknown.Stuff",
            "unknown",
            0.15,
            action="skipped",
            details={"reason": "unknown_media_type"},
        )

        # Get history
        history = db.get_processing_history(10)
        assert len(history) == 3

        # Verify record details
        if history:
            # Find the movie record
            movie_record = next(
                (r for r in history if r["media_type"] == "movie"), None
            )
            assert movie_record is not None
            assert movie_record["confidence"] == 0.95
            assert movie_record["action"] == "moved"
            assert movie_record["details"]["tmdb_match"] is True

            # Find the skipped records
            skipped_records = [r for r in history if r["action"] == "skipped"]
            assert len(skipped_records) == 2

        db.close()

    def test_cache_cleanup(self, temp_db_path):
        """Test cache cleanup functionality."""
        db = get_database(temp_db_path)

        # Add some cache entries
        db.set_tmdb_cache("movie:Test1:2020", "movie", "Test1", 2020, {"id": 1})
        db.set_tmdb_cache("movie:Test2:2020", "movie", "Test2", 2020, {"id": 2})

        # Verify entries exist
        assert db.get_tmdb_cache("movie:Test1:2020") is not None
        assert db.get_tmdb_cache("movie:Test2:2020") is not None

        # Clean old cache (should not remove anything since entries are new)
        db.clean_old_tmdb_cache(1)  # 1 day

        # Verify entries still exist
        assert db.get_tmdb_cache("movie:Test1:2020") is not None
        assert db.get_tmdb_cache("movie:Test2:2020") is not None

        db.close()

    def test_history_cleanup(self, temp_db_path):
        """Test history cleanup functionality."""
        db = get_database(temp_db_path)

        # Add some history records
        db.add_processing_record("/test1", "Test1", "movie", 0.8, "/dest1", "moved")
        db.add_processing_record("/test2", "Test2", "tv", 0.9, "/dest2", "moved")

        # Verify records exist
        history = db.get_processing_history(10)
        assert len(history) == 2

        # Clean old history (should not remove anything since entries are new)
        db.cleanup_old_history(1)  # 1 day

        # Verify records still exist
        history = db.get_processing_history(10)
        assert len(history) == 2

        db.close()

    @patch("mediamovarr.tmdb_client.requests.get")
    @patch("mediamovarr.database.MediaMovarrDB.get_tmdb_cache")
    @patch("mediamovarr.database.MediaMovarrDB.set_tmdb_cache")
    def test_tmdb_database_integration(
        self, mock_set_cache, mock_get_cache, mock_get, temp_db_path, mock_config
    ):
        """Test TMDb client with database caching."""
        from mediamovarr.tmdb_client import create_tmdb_client

        # Mock database cache - return None first (cache miss), then cached result
        mock_get_cache.side_effect = [
            None,
            {"title": "Inception", "release_date": "2010-07-16", "id": 27205},
        ]

        # Mock TMDb API responses
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"title": "Inception", "release_date": "2010-07-16", "id": 27205}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Create TMDb client with temporary database
        tmdb_client = create_tmdb_client(mock_config, temp_db_path)
        assert tmdb_client is not None

        # Test movie search with caching
        movie1 = tmdb_client.search_movie("Inception", 2010)
        assert movie1 is not None
        assert movie1["title"] == "Inception"

        # Verify cache was checked for first search
        mock_get_cache.assert_any_call("movie:Inception:2010")

        # Verify cache was set with the result
        mock_set_cache.assert_called_once()
        args = mock_set_cache.call_args[0]
        assert args[0] == "movie:Inception:2010"  # cache_key
        assert args[1] == "movie"  # search_type
        assert args[2] == "Inception"  # title
        assert args[3] == 2010  # year
        assert args[4] is not None  # result should not be None

        # Second search should hit database cache
        movie2 = tmdb_client.search_movie("Inception", 2010)
        assert movie2 == movie1

        # Verify API was called only once (first search)
        assert mock_get.call_count == 1

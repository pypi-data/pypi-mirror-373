"""Integration tests for MediaMovarr core functionality."""

import tempfile
from pathlib import Path

import pytest

from mediamovarr.classify import MediaType, classify_media
from mediamovarr.config import get_default_config
from mediamovarr.renamer import get_renamed_path


class TestIntegration:
    """Integration tests for core MediaMovarr functionality."""

    @pytest.fixture
    def temp_media_structure(self):
        """Create temporary media directory structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test config
            config = {
                "scan_dirs": [str(temp_path / "downloads")],
                "dest_dir": str(temp_path / "media"),
                "tmdb_enabled": False,
            }

            # Create test media folders
            downloads_dir = temp_path / "downloads"
            downloads_dir.mkdir()

            # TV show
            tv_folder = downloads_dir / "The Office Season 01"
            tv_folder.mkdir()
            (tv_folder / "episode1.mp4").touch()
            (tv_folder / "episode2.mp4").touch()

            # Movie
            movie_folder = downloads_dir / "Inception (2010)"
            movie_folder.mkdir()
            (movie_folder / "Inception.2010.1080p.mp4").touch()

            yield temp_path, config

    def test_basic_classification_and_renaming(self, temp_media_structure):
        """Test basic classification and renaming functionality."""
        temp_path, config = temp_media_structure
        downloads_dir = temp_path / "downloads"

        # Test TV show classification
        tv_folder = downloads_dir / "The Office Season 01"
        tv_type, tv_confidence, _ = classify_media(tv_folder)

        # Test movie classification
        movie_folder = downloads_dir / "Inception (2010)"
        movie_type, movie_confidence, _ = classify_media(movie_folder)

        # Verify classifications
        assert tv_type == MediaType.TV, f"Expected TV, got {tv_type}"
        assert movie_type == MediaType.MOVIE, f"Expected MOVIE, got {movie_type}"
        assert tv_confidence > 0.3, f"TV confidence too low: {tv_confidence}"
        assert movie_confidence > 0.3, f"Movie confidence too low: {movie_confidence}"

        # Test renaming
        tv_dest = get_renamed_path(tv_folder, tv_type, config)
        movie_dest = get_renamed_path(movie_folder, movie_type, config)

        # Verify destinations
        expected_tv_dest = temp_path / "media" / "TV Shows" / "The Office" / "Season 01"
        expected_movie_dest = temp_path / "media" / "Movies" / "Inception (2010)"

        assert (
            tv_dest == expected_tv_dest
        ), f"TV destination mismatch: {tv_dest} != {expected_tv_dest}"
        assert (
            movie_dest == expected_movie_dest
        ), f"Movie destination mismatch: {movie_dest} != {expected_movie_dest}"

    def test_end_to_end_workflow(self, temp_media_structure):
        """Test complete workflow from classification to destination."""
        temp_path, config = temp_media_structure
        downloads_dir = temp_path / "downloads"
        media_dir = temp_path / "media"

        # Process each folder
        test_folders = [
            ("The Office Season 01", MediaType.TV, "TV Shows/The Office/Season 01"),
            ("Inception (2010)", MediaType.MOVIE, "Movies/Inception (2010)"),
        ]

        for folder_name, expected_type, expected_relative_path in test_folders:
            folder_path = downloads_dir / folder_name

            # Classify
            media_type, confidence, _ = classify_media(folder_path)
            assert media_type == expected_type
            assert confidence > 0.3

            # Get destination
            dest_path = get_renamed_path(folder_path, media_type, config)
            assert (
                dest_path is not None
            ), f"get_renamed_path returned None for {folder_path}"

            expected_path = media_dir / expected_relative_path
            assert dest_path == expected_path

            # Just verify the path structure is correct (don't check if directories exist)
            assert str(dest_path).startswith(str(media_dir))

    def test_config_loading_integration(self):
        """Test that config loading works in integration context."""
        # Test default config
        default_config = get_default_config()
        assert isinstance(default_config, dict)
        assert "scan_dirs" in default_config
        assert "dest_dir" in default_config

        # Test that required keys exist
        required_keys = [
            "scan_dirs",
            "dest_dir",
            "tmdb_enabled",
            "confidence_thresholds",
        ]
        for key in required_keys:
            assert key in default_config, f"Missing required config key: {key}"

    def test_file_structure_detection(self, temp_media_structure):
        """Test that file structure detection works correctly."""
        temp_path, config = temp_media_structure
        downloads_dir = temp_path / "downloads"

        # TV show should have multiple video files
        tv_folder = downloads_dir / "The Office Season 01"
        tv_files = list(tv_folder.glob("*.mp4"))
        assert len(tv_files) == 2, f"Expected 2 TV files, found {len(tv_files)}"

        # Movie should have single video file
        movie_folder = downloads_dir / "Inception (2010)"
        movie_files = list(movie_folder.glob("*.mp4"))
        assert len(movie_files) == 1, f"Expected 1 movie file, found {len(movie_files)}"

        # Verify classifications still work
        tv_type, _, _ = classify_media(tv_folder)
        movie_type, _, _ = classify_media(movie_folder)

        assert tv_type == MediaType.TV
        assert movie_type == MediaType.MOVIE


if __name__ == "__main__":
    pytest.main([__file__])

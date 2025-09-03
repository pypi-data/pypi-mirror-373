"""Tests for media classification patterns and fixes."""

from pathlib import Path
from unittest.mock import patch

import pytest

from mediamovarr.classify import classify_media


class TestClassificationPatterns:
    """Test media classification patterns and fixes."""

    @pytest.fixture
    def mock_folder_info(self):
        """Mock folder info for consistent testing."""
        with patch("mediamovarr.classify.get_folder_info") as mock_info:
            mock_info.return_value = (
                1,
                0,
                0,
                3,
            )  # video_files, audio_files, subdirs, total_files
            yield mock_info

    def test_tv_show_sxxexx_patterns(self, mock_folder_info):
        """Test TV show classification with S##E## patterns."""
        test_cases = [
            "Arrow.S01E19.1080p.BluRay.x264-ROVERS",
            "The.Walking.Dead.S05E12.720p.HDTV.x264-KILLERS",
            "Game.of.Thrones.S08E06.1080p.WEB.H264-MEMENTO",
            "Friends.S01E01.1080p.BluRay.x264-PSYCHD",
            "Breaking.Bad.S02E13.720p.BluRay.x264-SiNNERS",
        ]

        for folder_name in test_cases:
            folder_path = Path(folder_name)
            media_type, confidence, _ = classify_media(folder_path)

            assert media_type == "tv", f"Failed to classify {folder_name} as TV show"
            assert (
                confidence >= 0.7
            ), f"Low confidence for TV show {folder_name}: {confidence}"

    def test_movie_classification_patterns(self, mock_folder_info):
        """Test that movies are still classified correctly."""
        test_cases = [
            "The.Dark.Knight.(2008).1080p.BluRay.x264-REFiNED",
            "Inception.(2010).720p.BluRay.x264-YIFY",
            "Avengers.Endgame.(2019).4K.UHD.BluRay.x265-TERMINAL",
        ]

        for folder_name in test_cases:
            folder_path = Path(folder_name)
            media_type, confidence, _ = classify_media(folder_path)

            assert media_type == "movie", f"Failed to classify {folder_name} as movie"
            assert (
                confidence >= 0.7
            ), f"Low confidence for movie {folder_name}: {confidence}"

    def test_season_episode_pattern_detection(self, mock_folder_info):
        """Test specific season/episode pattern detection."""
        # Test various S##E## patterns
        patterns = [
            "Show.S01E01",
            "Show.S1E1",
            "Show.S10E15",
            "Show.S01E01-E02",  # Multi-episode
            "Show.S01E01E02",  # Alternative format
        ]

        for pattern in patterns:
            folder_path = Path(pattern)
            media_type, confidence, _ = classify_media(folder_path)

            assert media_type == "tv", f"Failed to detect TV pattern: {pattern}"
            assert (
                confidence >= 0.8
            ), f"Low confidence for pattern {pattern}: {confidence}"

    def test_case_insensitive_patterns(self, mock_folder_info):
        """Test that patterns work case-insensitively."""
        test_cases = [
            "arrow.s01e19.1080p.bluray.x264-rovers",  # lowercase
            "THE.WALKING.DEAD.S05E12.720P.HDTV.X264-KILLERS",  # uppercase
            "Breaking.Bad.S02E13.720p.BluRay.x264-SiNNERS",  # mixed case
        ]

        for folder_name in test_cases:
            folder_path = Path(folder_name)
            media_type, confidence, _ = classify_media(folder_path)

            assert (
                media_type == "tv"
            ), f"Failed case-insensitive classification: {folder_name}"
            assert (
                confidence >= 0.7
            ), f"Low confidence for case variation {folder_name}: {confidence}"

    def test_tv_pattern_confidence_boost(self, mock_folder_info):
        """Test that TV patterns get appropriate confidence boost."""
        # Test that S##E## patterns get higher confidence than generic patterns
        generic_tv = Path("The Office Season 01")
        specific_tv = Path("The.Office.S01E01.1080p.BluRay")

        generic_type, generic_conf, _ = classify_media(generic_tv)
        specific_type, specific_conf, _ = classify_media(specific_tv)

        assert generic_type == "tv"
        assert specific_type == "tv"
        assert (
            specific_conf >= generic_conf
        ), "S##E## pattern should have higher confidence than generic season pattern"

    def test_movie_pattern_penalty_for_tv_keywords(self, mock_folder_info):
        """Test that movie detection is penalized when TV patterns are present."""
        # This should be classified as TV despite having movie-like elements
        ambiguous = Path("Movie.S01E01.1080p.BluRay")
        movie_type, movie_conf, _ = classify_media(ambiguous)

        assert (
            movie_type == "tv"
        ), "Should classify as TV when S##E## pattern is present"
        assert (
            movie_conf >= 0.8
        ), f"Should have high confidence for TV pattern: {movie_conf}"

    @pytest.mark.parametrize(
        "folder_name,expected_type,min_confidence",
        [
            ("Arrow.S01E19.1080p.BluRay.x264-ROVERS", "tv", 0.8),
            ("The.Dark.Knight.(2008).1080p.BluRay.x264-REFiNED", "movie", 0.7),
            ("The.Walking.Dead.S05E12.720p.HDTV.x264-KILLERS", "tv", 0.8),
            ("Inception.(2010).720p.BluRay.x264-YIFY", "movie", 0.7),
        ],
    )
    def test_parametrized_classification(
        self, mock_folder_info, folder_name, expected_type, min_confidence
    ):
        """Parametrized test for various classification scenarios."""
        folder_path = Path(folder_name)
        media_type, confidence, _ = classify_media(folder_path)

        assert (
            media_type == expected_type
        ), f"Expected {expected_type}, got {media_type} for {folder_name}"
        assert (
            confidence >= min_confidence
        ), f"Confidence too low for {folder_name}: {confidence}"


if __name__ == "__main__":
    pytest.main([__file__])

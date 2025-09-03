"""Tests for smart TMDb validation functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mediamovarr.classify import classify_media


class TestTMDbSmartValidation:
    """Test smart TMDb validation functionality."""

    @pytest.fixture
    def mock_tmdb_client(self):
        """Mock TMDb client for testing."""
        mock_client = MagicMock()
        return mock_client

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

    def test_tmdb_tv_show_boost(self, mock_tmdb_client, mock_folder_info):
        """Test that TMDb boosts confidence for matching TV show types."""
        # Mock TMDb responses - TV show found
        mock_tmdb_client.search_tv.return_value = {
            "name": "Arrow",
            "first_air_date": "2012-10-10",
            "id": 1412,
        }
        mock_tmdb_client.search_movie.return_value = None

        test_cases = [
            "Arrow.S01E19.1080p.BluRay.x264-ROVERS",
            "The.Walking.Dead.S05E12.720p.HDTV.x264-KILLERS",
            "Breaking.Bad.S02E13.720p.BluRay.x264-SiNNERS",
        ]

        for folder_name in test_cases:
            folder_path = Path(folder_name)
            media_type, confidence, tmdb_match = classify_media(
                folder_path, mock_tmdb_client
            )

            assert media_type == "tv", f"Failed to classify {folder_name} as TV show"
            assert tmdb_match, f"No TMDb match found for {folder_name}"
            assert (
                confidence >= 0.7
            ), f"Low confidence for TV show {folder_name}: {confidence}"

    def test_tmdb_movie_boost(self, mock_tmdb_client, mock_folder_info):
        """Test that TMDb boosts confidence for matching movie types."""
        # Mock TMDb responses - movie found
        mock_tmdb_client.search_movie.return_value = {
            "title": "Inception",
            "release_date": "2010-07-16",
            "id": 27205,
            "popularity": 50.0,
            "vote_average": 8.8,
        }
        mock_tmdb_client.search_tv_show.return_value = None

        test_cases = [
            "The.Dark.Knight.(2008).1080p.BluRay.x264-REFiNED",
            "Inception.(2010).720p.BluRay.x264-YIFY",
            "Avengers.Endgame.(2019).4K.UHD.BluRay.x265-TERMINAL",
        ]

        for folder_name in test_cases:
            folder_path = Path(folder_name)
            media_type, confidence, tmdb_match = classify_media(
                folder_path, mock_tmdb_client
            )

            assert media_type == "movie", f"Failed to classify {folder_name} as movie"
            assert tmdb_match, f"No TMDb match found for {folder_name}"
            assert (
                confidence >= 0.7
            ), f"Low confidence for movie {folder_name}: {confidence}"

    def test_tmdb_no_match_penalty(self, mock_tmdb_client, mock_folder_info):
        """Test that no TMDb match applies small penalty."""
        # Mock TMDb responses - nothing found
        mock_tmdb_client.search_tv_show.return_value = None
        mock_tmdb_client.search_movie.return_value = None

        folder_path = Path("Unknown.Show.S01E01.1080p")
        media_type, confidence, tmdb_match = classify_media(
            folder_path, mock_tmdb_client
        )

        assert not tmdb_match, "Should not have TMDb match for unknown content"
        # Confidence should still be reasonable even with penalty
        assert confidence >= 0.5, f"Confidence too low with no TMDb match: {confidence}"

    def test_tmdb_both_types_found(self, mock_tmdb_client, mock_folder_info):
        """Test behavior when both TV and movie matches are found."""
        # Mock TMDb responses - both found
        mock_tmdb_client.search_tv_show.return_value = {
            "name": "The Office",
            "first_air_date": "2005-03-24",
            "id": 2316,
            "popularity": 100.0,
            "vote_average": 8.7,
        }
        mock_tmdb_client.search_movie.return_value = {
            "title": "The Office",
            "release_date": "2025-01-01",  # Future date to make it less relevant
            "id": 12345,
            "popularity": 10.0,
            "vote_average": 6.0,
        }

        folder_path = Path("The.Office.S01E01.1080p")
        media_type, confidence, tmdb_match = classify_media(
            folder_path, mock_tmdb_client
        )

        assert tmdb_match, "Should have TMDb match when both types found"
        assert media_type == "tv", "Should prefer TV classification for episode pattern"
        assert (
            confidence >= 0.8
        ), f"Should have high confidence with TMDb match: {confidence}"

    def test_tmdb_confidence_boost_calculation(
        self, mock_tmdb_client, mock_folder_info
    ):
        """Test that TMDb boosts are calculated correctly."""
        # Mock TMDb responses - TV show found
        mock_tmdb_client.search_tv_show.return_value = {
            "name": "Breaking Bad",
            "first_air_date": "2008-01-20",
            "id": 1396,
            "popularity": 80.0,
            "vote_average": 9.5,
        }
        mock_tmdb_client.search_movie.return_value = None

        folder_path = Path("Breaking.Bad.S02E13.720p.BluRay.x264-SiNNERS")

        # Test with TMDb enhancement
        media_type_enhanced, confidence_enhanced, tmdb_match = classify_media(
            folder_path, mock_tmdb_client
        )

        # Test without TMDb (None client)
        media_type_base, confidence_base, _ = classify_media(folder_path, None)

        assert tmdb_match, "Should have TMDb match"
        assert (
            confidence_enhanced >= confidence_base
        ), "TMDb should boost or maintain confidence"
        assert (
            confidence_enhanced >= 0.7
        ), f"Enhanced confidence should be high: {confidence_enhanced}"
        assert (
            confidence_base >= 0.5
        ), f"Base confidence should be reasonable: {confidence_base}"

    def test_tmdb_validation_with_config(self, mock_folder_info):
        """Test TMDb validation with configuration loading."""
        # Mock config loading
        mock_config = {"tmdb_enabled": True, "tmdb_api_key": "test_key_123"}

        with patch("builtins.open"), patch(
            "json.load", return_value=mock_config
        ), patch("mediamovarr.tmdb_client.create_tmdb_client") as mock_create_client:
            mock_client = MagicMock()
            mock_client.search_tv_show.return_value = {
                "name": "Game of Thrones",
                "first_air_date": "2011-04-17",
                "id": 1399,
            }
            mock_client.search_movie.return_value = None
            mock_create_client.return_value = mock_client

            folder_path = Path("Game.of.Thrones.S08E06.1080p.WEB.H264-MEMENTO")
            media_type, confidence, tmdb_match = classify_media(
                folder_path, mock_client
            )

            assert media_type == "tv"
            assert tmdb_match
            assert confidence >= 0.7

    @pytest.mark.parametrize(
        "folder_name,expected_type,tmdb_tv_result,tmdb_movie_result",
        [
            (
                "Arrow.S01E19.1080p",
                "tv",
                {"name": "Arrow", "id": 1412, "popularity": 60.0, "vote_average": 7.5},
                None,
            ),
            (
                "Inception.(2010).720p",
                "movie",
                None,
                {
                    "title": "Inception",
                    "id": 27205,
                    "popularity": 50.0,
                    "vote_average": 8.8,
                },
            ),
            ("Ambiguous.Title.2020", "movie", None, None),  # No TMDb match
        ],
    )
    def test_parametrized_tmdb_scenarios(
        self,
        mock_tmdb_client,
        mock_folder_info,
        folder_name,
        expected_type,
        tmdb_tv_result,
        tmdb_movie_result,
    ):
        """Parametrized test for various TMDb scenarios."""
        mock_tmdb_client.search_tv_show.return_value = tmdb_tv_result
        mock_tmdb_client.search_movie.return_value = tmdb_movie_result

        folder_path = Path(folder_name)
        media_type, confidence, tmdb_match = classify_media(
            folder_path, mock_tmdb_client
        )

        assert media_type == expected_type
        assert confidence >= 0.5

        if tmdb_tv_result or tmdb_movie_result:
            assert tmdb_match
            assert confidence >= 0.7
        else:
            assert not tmdb_match


if __name__ == "__main__":
    pytest.main([__file__])

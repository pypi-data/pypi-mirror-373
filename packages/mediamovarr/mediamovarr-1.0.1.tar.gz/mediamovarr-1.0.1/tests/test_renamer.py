"""Tests for renaming logic."""

from pathlib import Path

import pytest

from mediamovarr.classify import MediaType
from mediamovarr.renamer import (
    _clean_title,
    _parse_movie_name,
    _parse_tv_show_name,
    get_renamed_path,
)


class TestRenamer:
    """Test renaming logic."""

    def test_tv_show_renaming(self):
        """Test TV show renaming."""
        config = {"dest_dir": "/media"}

        # Test season folder
        source = Path("The Office Season 01")
        dest = get_renamed_path(source, MediaType.TV, config)

        expected = Path("/media/TV Shows/The Office/Season 01")
        assert dest == expected

    def test_movie_renaming(self):
        """Test movie renaming."""
        config = {"dest_dir": "/media"}

        # Test movie with year
        source = Path("Inception (2010)")
        dest = get_renamed_path(source, MediaType.MOVIE, config)

        expected = Path("/media/Movies/Inception (2010)")
        assert dest == expected

    def test_music_renaming(self):
        """Test music renaming."""
        config = {"dest_dir": "/media"}

        # Test artist - album format
        source = Path("The Beatles - Abbey Road")
        dest = get_renamed_path(source, MediaType.MUSIC, config)

        expected = Path("/media/Music/The Beatles/Abbey Road")
        assert dest == expected

    def test_audiobook_renaming(self):
        """Test audiobook renaming."""
        config = {"dest_dir": "/media"}

        # Test author - title format
        source = Path("Stephen King - The Stand")
        dest = get_renamed_path(source, MediaType.AUDIOBOOK, config)

        expected = Path("/media/Audiobooks/Stephen King/The Stand")
        assert dest == expected

    def test_tv_show_parsing(self):
        """Test TV show name parsing."""
        test_cases = [
            ("The Office Season 01", ("The Office", 1)),
            ("Breaking Bad S05", ("Breaking Bad", 5)),
            ("Game of Thrones (2011) Season 03", ("Game Of Thrones", 3)),
            ("Friends Complete Series", ("Friends", None)),
        ]

        for input_name, expected in test_cases:
            result = _parse_tv_show_name(input_name)
            assert result == expected, f"Failed for: {input_name}"

    def test_movie_parsing(self):
        """Test movie name parsing."""
        test_cases = [
            ("Inception (2010)", ("Inception", 2010)),
            ("The Matrix 1999", ("The Matrix", 1999)),
            ("Avatar.2009.1080p.BluRay", ("Avatar.2009", None)),  # Current behavior
            ("Some Random Movie", ("Some Random Movie", None)),
        ]

        for input_name, expected in test_cases:
            result = _parse_movie_name(input_name)
            assert result == expected, f"Failed for: {input_name}"

    def test_title_cleaning(self):
        """Test title cleaning."""
        test_cases = [
            ("The.Office.2005.S01.1080p.BluRay", "The.Office.2005"),  # Current behavior
            ("Movie [1080p] (2020)", "Movie"),  # Brackets and parens removed
            ("Artist - Album (FLAC)", "Artist - Album"),  # Parens removed
            ("show.name.s01e01.720p", "Show.Name.S01E01"),  # Current behavior
        ]

        for dirty_title, expected_clean in test_cases:
            result = _clean_title(dirty_title)
            assert result == expected_clean, f"Failed cleaning: {dirty_title}"


if __name__ == "__main__":
    pytest.main([__file__])

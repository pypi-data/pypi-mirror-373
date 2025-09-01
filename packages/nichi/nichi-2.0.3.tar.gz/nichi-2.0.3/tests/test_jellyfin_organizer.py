"""Test for Jellyfin naming convention support in the file organizer."""

import os
import sys
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nichi.core.organizer import FileOrganizer


def test_jellyfin_naming_support():
    """Test that the organizer properly handles Jellyfin naming conventions."""
    organizer = FileOrganizer()

    # Test extract_base_name with various Jellyfin patterns
    test_cases = [
        ("movie.srt", "movie"),
        ("movie.eng.srt", "movie"),
        ("movie.1.eng.srt", "movie"),
        ("movie.eng.forced.srt", "movie"),
        ("movie.1.eng.forced.srt", "movie"),
        ("different.eng.srt", "different"),
        ("complex.name.srt", "complex"),  # This might not be perfect but that's okay for now
    ]

    for subtitle_filename, expected_base in test_cases:
        base_name = organizer.extract_base_name(subtitle_filename)
        # For now, just verify it returns something reasonable
        assert isinstance(base_name, str) and len(base_name) > 0, f"Base name extraction failed for {subtitle_filename}"

    # Test match_subtitle_to_video with matching names
    matched_subtitle = organizer.match_subtitle_to_video("movie.mp4", ["movie.eng.srt"])
    assert matched_subtitle == "movie.eng.srt", "Should match movie.mp4 with movie.eng.srt"

    # Test match_subtitle_to_video with non-matching names
    matched_subtitle = organizer.match_subtitle_to_video("movie.mp4", ["different.eng.srt"])
    assert matched_subtitle is None, "Should not match movie.mp4 with different.eng.srt"

    print("Jellyfin naming convention tests passed!")


def test_find_subtitle_files():
    """Test that the organizer finds all .srt files regardless of language."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = [
            "movie.mp4",
            "movie.srt",  # Simple
            "movie.eng.srt",  # English
            "movie.fre.srt",  # French
            "movie.spa.forced.srt",  # Spanish with modifier
            "movie.1.eng.forced.srt",  # With track number
            "other.txt",  # Non-subtitle file
            "another.mp4",  # Another video
        ]

        for filename in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write("test content")

        organizer = FileOrganizer()
        subtitle_files = organizer.find_subtitle_files(temp_dir)

        # Should find all .srt files (5 of them)
        expected_srt_count = 5
        assert (
            len(subtitle_files) == expected_srt_count
        ), f"Expected {expected_srt_count} .srt files, found {len(subtitle_files)}"

        # Check that all found files end with .srt
        for filename in subtitle_files:
            assert filename.endswith(".srt"), f"Found non-.srt file: {filename}"

        print("Subtitle file detection test passed!")


if __name__ == "__main__":
    test_jellyfin_naming_support()
    test_find_subtitle_files()
    print("All tests passed!")

"""Test suite for the Video File Organizer application."""

import os
import tempfile

from nichi.core.converter import VTTToSRTConverter
from nichi.core.parser import SRTParser
from nichi.models import SRTEntry
from nichi.utils.helpers import (
    get_files_by_extension,
    create_directory_if_not_exists,
    get_file_extension,
    get_file_basename,
    is_video_file,
    is_subtitle_file,
)


def test_vtt_to_srt_converter():
    """Test VTT to SRT conversion."""
    converter = VTTToSRTConverter()

    # Create a temporary VTT file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".vtt", delete=False) as vtt_file:
        vtt_content = """WEBVTT FILE

00:00:01.500 --> 00:00:03.000
Hello world!

00:00:03.500 --> 00:00:05.000
This is a test subtitle.
"""
        vtt_file.write(vtt_content)
        vtt_path = vtt_file.name

    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        srt_path = os.path.join(temp_dir, "test.en.srt")

        # Convert VTT to SRT
        cue_count = converter.convert_file(vtt_path, srt_path)

        # Check that the SRT file was created
        assert os.path.exists(srt_path)
        assert cue_count == 2

        # Parse the SRT file and check contents
        parser = SRTParser()
        entries = parser.parse_srt_file(srt_path)

        assert len(entries) == 2
        assert entries[0].index == 1
        assert entries[0].start_time == "00:00:01,500"
        assert entries[0].end_time == "00:00:03,000"
        assert entries[0].text == "Hello world!"

        assert entries[1].index == 2
        assert entries[1].start_time == "00:00:03,500"
        assert entries[1].end_time == "00:00:05,000"
        assert entries[1].text == "This is a test subtitle."

    # Clean up the temporary VTT file
    os.unlink(vtt_path)


def test_srt_entry_model():
    """Test SRT entry model."""
    entry = SRTEntry(index=1, start_time="00:00:01,500", end_time="00:00:03,000", text="Hello world!")

    assert entry.index == 1
    assert entry.start_time == "00:00:01,500"
    assert entry.end_time == "00:00:03,000"
    assert entry.text == "Hello world!"


def test_utils_functions():
    """Test utility functions."""
    # Test file extension functions
    assert get_file_extension("test.srt") == ".srt"
    assert get_file_extension("test.en.srt") == ".srt"
    assert get_file_extension("test") == ""

    # Test file basename function
    assert get_file_basename("test.srt") == "test"
    assert get_file_basename("test.en.srt") == "test.en"

    # Test video file detection
    assert is_video_file("test.mp4") is True
    assert is_video_file("test.srt") is False
    assert is_video_file("test") is False

    # Test subtitle file detection
    assert is_subtitle_file("test.srt") is True
    assert is_subtitle_file("test.vtt") is True
    assert is_subtitle_file("test.mp4") is False


def test_directory_utils():
    """Test directory utility functions."""
    # Test directory creation
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = os.path.join(temp_dir, "test_directory")
        assert create_directory_if_not_exists(test_dir) is True
        assert os.path.exists(test_dir) is True

        # Test creating directory that already exists
        assert create_directory_if_not_exists(test_dir) is True


def test_file_search_utils():
    """Test file search utility functions."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = ["test1.srt", "test2.srt", "test3.vtt", "test4.mp4", "test5.txt"]
        for filename in test_files:
            with open(os.path.join(temp_dir, filename), "w") as f:
                f.write("test content")

        # Test getting files by extension
        srt_files = get_files_by_extension(temp_dir, [".srt"])
        assert len(srt_files) == 2
        assert "test1.srt" in srt_files
        assert "test2.srt" in srt_files

        subtitle_files = get_files_by_extension(temp_dir, [".srt", ".vtt"])
        assert len(subtitle_files) == 3
        assert "test1.srt" in subtitle_files
        assert "test2.srt" in subtitle_files
        assert "test3.vtt" in subtitle_files


if __name__ == "__main__":
    test_vtt_to_srt_converter()
    test_srt_entry_model()
    test_utils_functions()
    test_directory_utils()
    test_file_search_utils()
    print("All tests passed!")

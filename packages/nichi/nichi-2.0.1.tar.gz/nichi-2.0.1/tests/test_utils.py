"""Test suite for the utils module."""

from nichi.utils.helpers import (
    get_files_by_extension,
    create_directory_if_not_exists,
    get_file_extension,
    get_file_basename,
    is_video_file,
    is_subtitle_file,
)
import os
import tempfile


def test_file_extension_functions():
    """Test file extension utility functions."""
    # Test get_file_extension
    assert get_file_extension("test.srt") == ".srt"
    assert get_file_extension("test.en.srt") == ".srt"
    assert get_file_extension("test") == ""
    assert get_file_extension("") == ""

    # Test get_file_basename
    assert get_file_basename("test.srt") == "test"
    assert get_file_basename("test.en.srt") == "test.en"
    assert get_file_basename("test") == "test"


def test_file_type_detection():
    """Test file type detection functions."""
    # Test is_video_file
    assert is_video_file("test.mp4") is True
    assert is_video_file("test.mkv") is True
    assert is_video_file("test.avi") is True
    assert is_video_file("test.srt") is False
    assert is_video_file("test") is False

    # Test is_subtitle_file
    assert is_subtitle_file("test.srt") is True
    assert is_subtitle_file("test.vtt") is True
    assert is_subtitle_file("test.sub") is True
    assert is_subtitle_file("test.mp4") is False
    assert is_subtitle_file("test") is False


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

        video_files = get_files_by_extension(temp_dir, [".mp4"])
        assert len(video_files) == 1
        assert "test4.mp4" in video_files


if __name__ == "__main__":
    test_file_extension_functions()
    test_file_type_detection()
    test_directory_utils()
    test_file_search_utils()
    print("Utils tests passed!")

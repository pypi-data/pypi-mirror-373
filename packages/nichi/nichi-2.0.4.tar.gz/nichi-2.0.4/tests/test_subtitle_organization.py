"""Test for subtitle organization fix."""

import os
import tempfile
import shutil
from nichi.core.organizer import FileOrganizer


def test_subtitle_organization_fix():
    """Test that all subtitle files are moved with their video."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files as described in the issue
        test_files = [
            "example.mp4",
            "example.en.srt",  # English subtitle
            "example.id.srt",  # Indonesian subtitle
            "example.en.sdh.srt"  # English SDH subtitle
        ]

        for filename in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write("test content")

        # Run the organizer
        organizer = FileOrganizer()
        result = organizer.organize_directory(temp_dir)
        
        # Check that a folder was created
        expected_folder = os.path.join(temp_dir, "example")
        assert os.path.exists(expected_folder), "Folder 'example' should be created"
        
        # Check that all files were moved to the folder
        for filename in test_files:
            file_path = os.path.join(expected_folder, filename)
            assert os.path.exists(file_path), f"File {filename} should be moved to the folder"
            
        print("Subtitle organization fix test passed!")


if __name__ == "__main__":
    test_subtitle_organization_fix()
    print("All tests passed!")
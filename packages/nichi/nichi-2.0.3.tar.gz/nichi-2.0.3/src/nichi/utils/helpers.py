"""Utility functions for the Video File Organizer application."""

import os
from pathlib import Path
from typing import List

from nichi.constants import VIDEO_EXTENSIONS, SUBTITLE_EXTENSIONS


def get_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """
    Get all files in a directory with specified extensions.

    Args:
        directory: Directory to search
        extensions: List of file extensions (e.g., ['.srt', '.vtt'])

    Returns:
        List of filenames with matching extensions
    """
    try:
        items = os.listdir(directory)
        return [item for item in items if any(item.lower().endswith(ext.lower()) for ext in extensions)]
    except Exception:
        return []


def create_directory_if_not_exists(directory_path: str) -> bool:
    """
    Create a directory if it doesn't exist.

    Args:
        directory_path: Path to the directory to create

    Returns:
        True if directory was created or already existed, False on error
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.

    Args:
        filename: Name of the file

    Returns:
        File extension (e.g., '.srt', '.vtt')
    """
    return Path(filename).suffix.lower()


def get_file_basename(filename: str) -> str:
    """
    Get the base name of a file without extension.

    Args:
        filename: Name of the file

    Returns:
        Base name without extension
    """
    return Path(filename).stem


def is_video_file(filename: str) -> bool:
    """
    Check if a file is a video file based on its extension.

    Args:
        filename: Name of the file

    Returns:
        True if the file is a video file, False otherwise
    """
    return get_file_extension(filename) in VIDEO_EXTENSIONS


def is_subtitle_file(filename: str) -> bool:
    """
    Check if a file is a subtitle file based on its extension.

    Args:
        filename: Name of the file

    Returns:
        True if the file is a subtitle file, False otherwise
    """
    return get_file_extension(filename) in SUBTITLE_EXTENSIONS

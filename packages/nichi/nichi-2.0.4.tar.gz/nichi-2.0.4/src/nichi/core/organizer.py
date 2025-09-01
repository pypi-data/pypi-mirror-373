"""File organizer module for grouping video and subtitle files."""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from nichi.constants import EXT_MP4, EXT_SRT
from nichi.models import FileProcessingResult


class FileOrganizer:
    """Organizes MP4 files with their corresponding subtitle files into folders."""

    def __init__(self) -> None:
        """Initialize the file organizer."""
        self.processed_files: List[str] = []

    def find_video_files(self, directory_path: str) -> List[str]:
        """
        Find all MP4 files in the specified directory.

        Args:
            directory_path: Path to search for MP4 files

        Returns:
            List of MP4 filenames
        """
        all_files = os.listdir(directory_path)
        video_files = []
        for filename in all_files:
            if filename.lower().endswith(EXT_MP4):
                video_files.append(filename)
        return video_files

    def find_subtitle_files(self, directory_path: str) -> List[str]:
        """
        Find all subtitle files in the specified directory.

        Args:
            directory_path: Path to search for subtitle files

        Returns:
            List of subtitle filenames (.srt files including all language codes)
        """
        all_files = os.listdir(directory_path)
        subtitle_files = []
        for filename in all_files:
            if filename.lower().endswith(EXT_SRT):
                subtitle_files.append(filename)
        return subtitle_files

    def extract_base_name(self, filename: str) -> str:
        """
        Extract base name from filename using Jellyfin naming convention.

        Args:
            filename: The filename to extract base name from

        Returns:
            Base name without language/track/modifier information
        """
        # Import here to avoid circular import
        from nichi.services.jellyfin import JellyfinParser

        # Parse the filename using Jellyfin parser
        parsed = JellyfinParser.parse_filename(filename)
        name_value = parsed["name"]

        # If we can't parse it properly, fall back to simple extension removal
        if name_value:
            return name_value
        else:
            # Fall back to removing just the extension
            file_parts = os.path.splitext(filename)
            base_name = file_parts[0]
            return base_name

    def match_subtitle_to_video(self, video_filename: str, subtitle_files: List[str]) -> List[str]:
        """
        Find matching subtitle files for a video file.

        Args:
            video_filename: Name of the video file
            subtitle_files: List of available subtitle files

        Returns:
            List of matching subtitle filenames
        """
        video_parts = os.path.splitext(video_filename)
        video_base_name = video_parts[0]
        
        matching_subtitles = []
        for subtitle_file in subtitle_files:
            subtitle_base_name = self.extract_base_name(subtitle_file)
            if subtitle_base_name == video_base_name:
                matching_subtitles.append(subtitle_file)

        return matching_subtitles

    def group_files(self, directory_path: str) -> Dict[str, List[str]]:
        """
        Group MP4 files with their matching subtitle files.

        Args:
            directory_path: Directory path to scan for files

        Returns:
            Dictionary mapping MP4 filenames to their matching subtitle files
        """
        video_files = self.find_video_files(directory_path)
        subtitle_files = self.find_subtitle_files(directory_path)

        file_pairs: Dict[str, List[str]] = {}

        for video_file in video_files:
            matching_subtitles = self.match_subtitle_to_video(video_file, subtitle_files)
            file_pairs[video_file] = matching_subtitles

        used_subtitles = set()
        for subtitles in file_pairs.values():
            for subtitle in subtitles:
                used_subtitles.add(subtitle)

        for subtitle_file in subtitle_files:
            if subtitle_file not in used_subtitles:
                subtitle_base_name = self.extract_base_name(subtitle_file)
                placeholder_video = "%s%s" % (subtitle_base_name, EXT_MP4)

                if placeholder_video not in file_pairs:
                    file_pairs[placeholder_video] = [subtitle_file]
                else:
                    file_pairs[placeholder_video].append(subtitle_file)

        return file_pairs

    def create_folder_structure(self, directory_path: str, file_pairs: Dict[str, List[str]]) -> List[str]:
        """
        Create folder structure and move files into appropriate folders.

        Args:
            directory_path: Base directory path
            file_pairs: Dictionary mapping video files to subtitle files

        Returns:
            List of created folder names
        """
        created_folders: List[str] = []

        pair_items = file_pairs.items()
        for video_filename, subtitle_filenames in pair_items:
            video_parts = os.path.splitext(video_filename)
            folder_base_name = video_parts[0]
            folder_path = os.path.join(directory_path, folder_base_name)

            path_object = Path(folder_path)
            path_object.mkdir(exist_ok=True)
            created_folders.append(folder_base_name)

            video_source_path = os.path.join(directory_path, video_filename)
            source_exists = os.path.exists(video_source_path)
            if source_exists:
                video_destination_path = os.path.join(folder_path, video_filename)
                shutil.move(video_source_path, video_destination_path)
                move_message = "Moved video: %s" % video_filename
                self.processed_files.append(move_message)

            for subtitle_filename in subtitle_filenames:
                if subtitle_filename:
                    subtitle_source_path = os.path.join(directory_path, subtitle_filename)
                    subtitle_exists = os.path.exists(subtitle_source_path)
                    if subtitle_exists:
                        subtitle_destination_path = os.path.join(folder_path, subtitle_filename)
                        shutil.move(subtitle_source_path, subtitle_destination_path)
                        move_message = "Moved subtitle: %s" % subtitle_filename
                        self.processed_files.append(move_message)

        return created_folders

    def organize_directory(self, directory_path: str) -> FileProcessingResult:
        """
        Complete organization process for a directory.

        Args:
            directory_path: Directory to organize

        Returns:
            FileProcessingResult containing organization results
        """
        self.processed_files = []

        file_pairs = self.group_files(directory_path)
        created_folders = self.create_folder_structure(directory_path, file_pairs)

        result = FileProcessingResult(
            created_folders=created_folders,
            processed_files=self.processed_files,
        )
        return result

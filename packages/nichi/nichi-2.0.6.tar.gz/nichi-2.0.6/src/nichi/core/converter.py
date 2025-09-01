"""VTT to SRT converter module."""

import os
from pathlib import Path
from typing import List, Optional, Tuple

from nichi.constants import EXT_EN_SRT, EXT_VTT


class VTTToSRTConverter:
    """Converter class for WebVTT to SRT subtitle format conversion."""

    def __init__(self) -> None:
        """Initialize the VTT to SRT converter."""
        self.cue_count = 0

    def format_timestamp(self, timestamp: str) -> str:
        """
        Convert WebVTT timestamp to SRT format.

        Args:
            timestamp: WebVTT timestamp string (e.g., '00:01:02.5', '01:02:03.456')

        Returns:
            Formatted SRT timestamp string (HH:MM:SS,mmm)
        """
        normalized_timestamp = timestamp.replace(",", ".").strip()
        parts = normalized_timestamp.split(":")

        if len(parts) == 2:
            hours = 0
            minutes = int(parts[0])
            seconds_part = parts[1]
        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds_part = parts[2]
        else:
            return "00:00:00,000"

        if "." in seconds_part:
            split_result = seconds_part.split(".", 1)
            seconds_string = split_result[0]
            milliseconds_string = split_result[1]
            seconds = int(seconds_string)
            padded_milliseconds = (milliseconds_string + "000")[:3]
            milliseconds = int(padded_milliseconds)
        else:
            seconds = int(seconds_part)
            milliseconds = 0

        formatted_time = "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, milliseconds)
        return formatted_time

    def parse_vtt_content(self, content: str) -> List[Tuple[str, str, str]]:
        """
        Parse VTT content and extract cues.

        Args:
            content: Raw VTT file content

        Returns:
            List of tuples containing (start_time, end_time, text)
        """
        content_with_lf = content.replace("\r\n", "\n")
        normalized_content = content_with_lf.replace("\r", "\n")
        lines = normalized_content.split("\n")

        cues: List[Tuple[str, str, str]] = []
        line_pointer = 0

        while line_pointer < len(lines):
            # Skip empty lines
            while line_pointer < len(lines) and lines[line_pointer].strip() == "":
                line_pointer += 1

            if line_pointer >= len(lines):
                break

            current_line = lines[line_pointer].strip()

            if current_line.startswith("WEBVTT"):
                line_pointer += 1
                continue

            note_styles = ("NOTE", "STYLE", "REGION")
            if current_line.startswith(note_styles):
                line_pointer += 1
                while line_pointer < len(lines) and lines[line_pointer].strip() != "":
                    line_pointer += 1
                continue

            if "-->" not in lines[line_pointer] and lines[line_pointer].strip() != "":
                line_pointer += 1

            if line_pointer >= len(lines) or "-->" not in lines[line_pointer]:
                line_pointer += 1
                continue

            timestamp_line = lines[line_pointer]
            line_pointer += 1

            if "-->" in timestamp_line:
                timestamp_parts = timestamp_line.split("-->", 1)
                start_raw = timestamp_parts[0].strip()
                end_part = timestamp_parts[1].strip()
                end_raw_parts = end_part.split(" ", 1)
                end_raw = end_raw_parts[0].strip()

                start_time = self.format_timestamp(start_raw)
                end_time = self.format_timestamp(end_raw)
            else:
                line_pointer += 1
                continue

            text_lines = []
            while line_pointer < len(lines) and lines[line_pointer].strip() != "":
                text_lines.append(lines[line_pointer])
                line_pointer += 1

            joined_text = "\n".join(text_lines)
            cues.append((start_time, end_time, joined_text))

        return cues

    def generate_srt_content(self, cues: List[Tuple[str, str, str]]) -> str:
        """
        Generate SRT format content from cues.

        Args:
            cues: List of tuples containing (start_time, end_time, text)

        Returns:
            Complete SRT formatted content string
        """
        srt_lines = []
        cue_index = 1

        for start_time, end_time, subtitle_text in cues:
            index_line = str(cue_index)
            srt_lines.append(index_line)

            time_line = "%s --> %s" % (start_time, end_time)
            srt_lines.append(time_line)

            if subtitle_text:
                srt_lines.append(subtitle_text)

            srt_lines.append("")
            cue_index += 1

        joined_lines = "\n".join(srt_lines)
        stripped_lines = joined_lines.rstrip()
        result = "%s\n" % stripped_lines
        return result

    def convert_file(self, source_path: str, destination_path: str) -> int:
        """
        Convert a single VTT file to SRT format.

        Args:
            source_path: Path to the source VTT file
            destination_path: Path where the SRT file will be saved

        Returns:
            Number of subtitle cues converted
        """
        with open(source_path, "r", encoding="utf-8-sig") as file:
            content = file.read()

        cues = self.parse_vtt_content(content)
        srt_content = self.generate_srt_content(cues)

        with open(destination_path, "w", encoding="utf-8") as file:
            file.write(srt_content)

        cue_count = len(cues)
        self.cue_count = cue_count
        return cue_count

    def convert_directory(self, directory_path: str, output_directory: Optional[str] = None) -> List[Tuple[str, int]]:
        """
        Convert all VTT files in a directory to SRT format.

        Args:
            directory_path: Directory containing VTT files
            output_directory: Directory where SRT files will be saved (optional)

        Returns:
            List of tuples containing (filename, cue_count) for each converted file
        """
        if output_directory is None:
            output_directory = directory_path

        output_path = Path(output_directory)
        output_path.mkdir(exist_ok=True)

        all_files = os.listdir(directory_path)
        vtt_files = []
        for filename in all_files:
            if filename.lower().endswith(EXT_VTT):
                vtt_files.append(filename)

        converted_files: List[Tuple[str, int]] = []

        for vtt_filename in vtt_files:
            file_parts = os.path.splitext(vtt_filename)
            base_name = file_parts[0]
            source_path = os.path.join(directory_path, vtt_filename)
            destination_filename = "%s%s" % (base_name, EXT_EN_SRT)
            destination_path = os.path.join(output_directory, destination_filename)

            path_exists = os.path.exists(destination_path)
            if path_exists:
                continue

            cue_count = self.convert_file(source_path, destination_path)
            file_info = (vtt_filename, cue_count)
            converted_files.append(file_info)

        return converted_files

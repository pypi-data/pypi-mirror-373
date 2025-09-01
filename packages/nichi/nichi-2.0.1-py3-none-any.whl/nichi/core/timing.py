"""SRT timing adjustment utility."""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from nichi.models import SRTEntry


class SRTTimingAdjuster:
    """Utility for adjusting SRT subtitle timing."""

    @staticmethod
    def parse_srt_time(time_str: str) -> timedelta:
        """
        Parse SRT time format (HH:MM:SS,mmm) to timedelta.

        Args:
            time_str: Time string in format "HH:MM:SS,mmm"

        Returns:
            timedelta object
        """
        # Parse format: HH:MM:SS,mmm
        time_pattern = r"(\d{2}):(\d{2}):(\d{2}),(\d{3})"
        match = re.match(time_pattern, time_str)
        if not match:
            error_message = "Invalid time format: %s" % time_str
            raise ValueError(error_message)

        match_groups = match.groups()
        hours = int(match_groups[0])
        minutes = int(match_groups[1])
        seconds = int(match_groups[2])
        milliseconds = int(match_groups[3])

        time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
        return time_delta

    @staticmethod
    def format_srt_time(td: timedelta) -> str:
        """
        Format timedelta back to SRT time format.

        Args:
            td: timedelta object

        Returns:
            Time string in format "HH:MM:SS,mmm"
        """
        # Handle negative times by setting to 00:00:00,000
        total_seconds_value = td.total_seconds()
        if total_seconds_value < 0:
            return "00:00:00,000"

        total_seconds = int(total_seconds_value)
        microseconds = int(td.microseconds)
        milliseconds = int(microseconds / 1000)

        hours = total_seconds // 3600
        remaining_seconds = total_seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60

        # Ensure we don't exceed 23:59:59,999
        if hours > 23:
            hours = 23
            minutes = 59
            seconds = 59
            milliseconds = 999

        formatted_time = "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, milliseconds)
        return formatted_time

    @staticmethod
    def adjust_timing(time_str: str, offset_ms: int) -> str:
        """
        Adjust a single time string by offset in milliseconds.

        Args:
            time_str: Original time string
            offset_ms: Offset in milliseconds (positive or negative)

        Returns:
            Adjusted time string
        """
        try:
            original_time = SRTTimingAdjuster.parse_srt_time(time_str)
            offset = timedelta(milliseconds=offset_ms)
            adjusted_time = original_time + offset
            formatted_time = SRTTimingAdjuster.format_srt_time(adjusted_time)
            return formatted_time
        except ValueError:
            # Return original if parsing fails
            return time_str

    @staticmethod
    def adjust_srt_entries(entries: List[SRTEntry], offset_ms: int) -> List[SRTEntry]:
        """
        Adjust timing for all SRT entries.

        Args:
            entries: List of SRTEntry objects
            offset_ms: Offset in milliseconds (positive or negative)

        Returns:
            List of adjusted SRTEntry objects
        """
        adjusted_entries = []

        for entry in entries:
            # Create new entry with adjusted times
            start_time_adjusted = SRTTimingAdjuster.adjust_timing(entry.start_time, offset_ms)
            end_time_adjusted = SRTTimingAdjuster.adjust_timing(entry.end_time, offset_ms)
            adjusted_entry = SRTEntry(
                index=entry.index,
                start_time=start_time_adjusted,
                end_time=end_time_adjusted,
                text=entry.text,
            )
            adjusted_entries.append(adjusted_entry)

        return adjusted_entries

    @staticmethod
    def get_backup_filename(input_path: str) -> str:
        """
        Generate a backup filename that won't be detected by media servers.

        Args:
            input_path: Path to the original file

        Returns:
            Path for the backup file
        """
        input_file = Path(input_path)

        # Start with .old extension
        file_suffix = input_file.suffix
        old_suffix = "%s.old" % file_suffix
        backup_path = input_file.with_suffix(old_suffix)

        # If that exists, try .old.1, .old.2, etc.
        counter = 1
        path_exists = backup_path.exists()
        while path_exists:
            counter_suffix = "%s.old.%d" % (file_suffix, counter)
            backup_path = input_file.with_suffix(counter_suffix)
            counter += 1
            path_exists = backup_path.exists()

            # Safety check to prevent infinite loop
            if counter > 100:
                # Use timestamp as fallback
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                timestamp_suffix = "%s.old.%s" % (file_suffix, timestamp)
                backup_path = input_file.with_suffix(timestamp_suffix)
                break

        return str(backup_path)

    @staticmethod
    def adjust_srt_file_with_backup(input_path: str, offset_ms: int) -> Tuple[bool, str, int, str]:
        """
        Adjust timing for an entire SRT file, backing up original with .old extension.

        Args:
            input_path: Path to input SRT file
            offset_ms: Offset in milliseconds (positive or negative)

        Returns:
            Tuple of (success: bool, message: str, entries_processed: int, backup_filename: str)
        """
        try:
            import shutil

            # Import here to avoid circular imports
            from nichi.core.parser import SRTParser

            # Generate backup filename that won't conflict with media servers
            backup_path = SRTTimingAdjuster.get_backup_filename(input_path)

            # Parse the original file
            entries = SRTParser.parse_srt_file(input_path)
            if not entries:
                return False, "No valid subtitle entries found", 0, ""

            # Create backup of original file
            shutil.copy2(input_path, backup_path)

            # Adjust timing
            adjusted_entries = SRTTimingAdjuster.adjust_srt_entries(entries, offset_ms)

            # Write the adjusted file to the original location
            SRTParser.write_srt_file(adjusted_entries, input_path)

            offset_seconds = offset_ms / 1000
            direction = "forward" if offset_ms > 0 else "backward"
            abs_offset = abs(offset_seconds)
            message = "Adjusted %d entries by %.3fs %s" % (len(adjusted_entries), abs_offset, direction)

            backup_name = Path(backup_path).name
            return True, message, len(adjusted_entries), backup_name

        except Exception as e:
            error_message = "Error adjusting timing: %s" % str(e)
            return False, error_message, 0, ""

    @staticmethod
    def validate_offset(offset_input: str) -> Optional[int]:
        """
        Validate and convert offset input to milliseconds.

        Args:
            offset_input: User input string

        Returns:
            Offset in milliseconds or None if invalid
        """
        try:
            stripped_input = offset_input.strip()
            float_value = float(stripped_input)
            offset_ms = int(float_value)
            # Limit to reasonable range (±10 minutes)
            max_offset = 10 * 60 * 1000  # 10 minutes in ms
            abs_offset = abs(offset_ms)
            if abs_offset > max_offset:
                return None
            return offset_ms
        except (ValueError, TypeError):
            return None

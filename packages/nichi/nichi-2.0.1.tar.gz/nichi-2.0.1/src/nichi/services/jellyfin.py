"""Jellyfin subtitle filename parser."""

from pathlib import Path
from typing import Dict, Optional


class JellyfinParser:
    """Simple Jellyfin subtitle filename parser."""

    MODIFIERS = {"sdh", "forced", "cc", "hi"}

    @staticmethod
    def parse_filename(filename: str) -> Dict[str, Optional[str]]:
        """
        Parse Jellyfin subtitle filename.

        Logic:
        - Split filename into parts
        - Determine language position based on part count
        - Extract name, track, language, and modifier
        """
        path = Path(filename)
        extension = path.suffix
        stem = path.stem
        parts = stem.split(".")
        part_count = len(parts)

        # Initialize result
        result = {
            "name": None,
            "track": None,
            "language": None,
            "modifier": None,
            "extension": extension,
        }

        if part_count < 2:
            # Not a valid jellyfin subtitle
            name_value = parts[0] if parts else None
            result["name"] = name_value
            return result

        if part_count == 2:
            # name.language.srt
            result["name"] = parts[0]
            result["language"] = parts[1]

        elif part_count == 3:
            # name.track.language.srt OR name.language.modifier.srt
            third_part = parts[2]
            if third_part in JellyfinParser.MODIFIERS:
                # name.language.modifier.srt
                result["name"] = parts[0]
                result["language"] = parts[1]
                result["modifier"] = third_part
            else:
                # name.track.language.srt
                result["name"] = parts[0]
                result["track"] = parts[1]
                result["language"] = third_part

        elif part_count == 4:
            # name.track.language.modifier.srt
            result["name"] = parts[0]
            result["track"] = parts[1]
            result["language"] = parts[2]
            result["modifier"] = parts[3]

        elif part_count >= 5:
            # name.extra.track.language.modifier.srt (language is 3rd from last)
            language_index = part_count - 3
            name_end_index = language_index - 1
            name_parts = parts[:name_end_index]
            result["name"] = ".".join(name_parts)
            result["track"] = parts[name_end_index]
            result["language"] = parts[language_index]
            modifier_index = language_index + 1
            result["modifier"] = parts[modifier_index]

        return result

    @staticmethod
    def format_output_filename(input_filename: str, target_language: str) -> str:
        """Generate output filename with target language."""
        parsed = JellyfinParser.parse_filename(input_filename)

        parts = []
        name_value = parsed["name"]
        if name_value:
            parts.append(name_value)

        track_value = parsed["track"]
        if track_value:
            parts.append(track_value)

        parts.append(target_language)

        modifier_value = parsed["modifier"]
        if modifier_value:
            parts.append(modifier_value)

        joined_parts = ".".join(parts)
        extension = parsed["extension"]
        if extension:
            result = "%s%s" % (joined_parts, extension)
        else:
            result = "%s.srt" % joined_parts
        return result

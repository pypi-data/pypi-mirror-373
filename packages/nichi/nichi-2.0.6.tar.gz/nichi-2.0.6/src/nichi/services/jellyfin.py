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
            # Check if the third part is a modifier
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

        elif part_count >= 4:
            # For complex cases, we need to identify the language position
            # Language is typically the part before the last modifier
            # or second to last part if there's a modifier

            # Check if the last part is a modifier
            last_part = parts[-1]
            if last_part in JellyfinParser.MODIFIERS:
                # Has modifier
                result["modifier"] = last_part
                # Language is the part before modifier
                language_index = part_count - 2
                result["language"] = parts[language_index]
                # Track is the part before language if there's a track
                if language_index >= 2:
                    result["track"] = parts[language_index - 1]
                    # Name is everything before track
                    result["name"] = ".".join(parts[: language_index - 1])
                else:
                    # No track, name is everything before language
                    result["name"] = ".".join(parts[:language_index])
            else:
                # No modifier, language is the last part
                result["language"] = last_part
                # Track is the part before language if there's a track
                if part_count >= 3:
                    result["track"] = parts[part_count - 2]
                    # Name is everything before track
                    result["name"] = ".".join(parts[: part_count - 2])
                else:
                    # No track, name is everything before language
                    result["name"] = ".".join(parts[: part_count - 1])

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

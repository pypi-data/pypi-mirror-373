"""SRT file parser and writer utilities."""

import re
from typing import List

from nichi.models import SRTEntry


class SRTParser:
    """Simple SRT file parser."""

    @staticmethod
    def parse_srt_file(file_path: str) -> List[SRTEntry]:
        """Parse SRT file and return list of entries."""
        entries = []

        # Try different encodings to read the file
        content = None
        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as file:
                    content = file.read()
                break
            except UnicodeDecodeError:
                continue

        if not content:
            return entries

        # Normalize newline characters and remove leading/trailing whitespace.
        # This ensures consistent splitting regardless of file's line endings (\n or \r\n).
        normalized_content = content.replace("\r\n", "\n").strip()

        # Split the content into blocks. The key change is the regular expression here.
        # It now splits on two or more newlines ONLY IF they are followed by a digit
        # (which indicates the start of the next subtitle index).
        # The `(?=...)` is a positive lookahead that checks without consuming the characters.
        # This prevents splitting on blank lines within a subtitle's text.
        blocks = re.split(r"\n{2,}(?=\d+\s*\n)", normalized_content)

        for block in blocks:
            if not block.strip():
                continue

            lines = block.strip().split("\n")
            # A valid entry needs at least an index, a timestamp, and text.
            if len(lines) < 3:
                continue

            try:
                index = int(lines[0])

                # Parse time line.
                # The regex now accepts both comma (,) and dot (.) for milliseconds.
                time_pattern = r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})"
                time_match = re.match(time_pattern, lines[1])
                if not time_match:
                    continue

                # Ensure milliseconds are consistently stored with a comma
                raw_start_time = time_match.group(1)
                start_time = raw_start_time.replace(".", ",")
                raw_end_time = time_match.group(2)
                end_time = raw_end_time.replace(".", ",")

                # Join all subsequent lines to form the text, preserving newlines.
                text_lines = lines[2:]
                text = "\n".join(text_lines).strip()

                subtitle_entry = SRTEntry(index=index, start_time=start_time, end_time=end_time, text=text)
                entries.append(subtitle_entry)

            except (ValueError, IndexError):
                # Skip malformed blocks
                continue

        return entries

    @staticmethod
    def write_srt_file(entries: List[SRTEntry], file_path: str):
        """Write SRT entries to file."""
        with open(file_path, "w", encoding="utf-8") as file:
            for entry in entries:
                index_line = "%d\n" % entry.index
                time_line = "%s --> %s\n" % (entry.start_time, entry.end_time)
                text_line = "%s\n\n" % entry.text

                file.write(index_line)
                file.write(time_line)
                file.write(text_line)

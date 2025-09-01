"""Main SRT translator combining all components."""

from pathlib import Path
from typing import Callable, Dict, Optional

from nichi.constants import DEFAULT_TARGET_LANGUAGE
from nichi.core.parser import SRTParser
from nichi.models import SRTEntry, TranslationResult
from nichi.services.gemini import GeminiTranslator
from nichi.services.jellyfin import JellyfinParser


class SRTTranslator:
    """Main SRT translation class."""

    def __init__(self):
        self.parser = SRTParser()
        self.translator = GeminiTranslator()
        self.formatter = JellyfinParser()

    def get_available_languages(self) -> Dict[str, str]:
        """Get available language codes and names."""
        languages = self.translator.LANGUAGES.copy()
        return languages

    def get_default_target_language(self) -> str:
        """Get default target language from environment."""
        from nichi.config.config import config

        default_language = config.get_config_value("DEFAULT_TARGET_LANGUAGE", DEFAULT_TARGET_LANGUAGE)
        return default_language

    def detect_source_language(self, filename: str) -> Optional[str]:
        """Detect source language from filename."""
        parsed = self.formatter.parse_filename(filename)
        language = parsed["language"]
        return language

    def translate_file(
        self,
        input_path: str,
        target_language: str,
        source_language: str = None,
        output_path: str = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> TranslationResult:
        """
        Translate an SRT file.

        Returns:
            TranslationResult object with translation details
        """
        input_file = Path(input_path)

        file_exists = input_file.exists()
        if not file_exists:
            error_message = "Input file not found: %s" % input_path
            raise FileNotFoundError(error_message)

        # Parse SRT file
        entries = self.parser.parse_srt_file(input_path)
        if not entries:
            raise ValueError("No valid subtitle entries found")

        # Determine output path
        if output_path is None:
            output_filename = self.formatter.format_output_filename(input_file.name, target_language)
            output_path = input_file.parent / output_filename
        else:
            path_object = Path(output_path)
            output_filename = path_object.name

        # Extract texts for translation
        texts = [entry.text for entry in entries]

        # Translate texts
        translated_texts = self.translator.translate_texts(texts, target_language, source_language, progress_callback)

        # Create translated entries
        translated_entries = []
        entries_and_translations = zip(entries, translated_texts)
        for entry, translated_text in entries_and_translations:
            translated_entry = SRTEntry(
                index=entry.index,
                start_time=entry.start_time,
                end_time=entry.end_time,
                text=translated_text,
            )
            translated_entries.append(translated_entry)

        # Write output file
        output_path_str = str(output_path)
        self.parser.write_srt_file(translated_entries, output_path_str)

        result = TranslationResult(
            input_file=str(input_file.name),
            output_file=output_filename,
            total_entries=len(entries),
            translated_entries=len(translated_entries),
            target_language=target_language,
            source_language=source_language,
        )
        return result

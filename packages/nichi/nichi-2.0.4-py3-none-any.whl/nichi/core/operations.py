"""Core operations for the video organizer."""

from rich.console import Console
from rich.panel import Panel

from nichi.core.converter import VTTToSRTConverter
from nichi.core.files import FileOperations
from nichi.core.organizer import FileOrganizer
from nichi.core.timing import SRTTimingAdjuster
from nichi.core.translation import TranslationOperations
from nichi.core.translator import SRTTranslator
from nichi.ui.components import UIComponents
from nichi.ui.input import UserInput


class Operations:
    """Core operations for file handling."""

    def __init__(
        self,
        converter: VTTToSRTConverter,
        organizer: FileOrganizer,
        translator: SRTTranslator,
        timing_adjuster: SRTTimingAdjuster,
        console: Console,
    ):
        self.console = console
        self.ui = UIComponents(console)
        self.input_handler = UserInput(console)

        # Initialize operation components
        self.file_ops = FileOperations(converter, organizer, timing_adjuster, console, self.ui, self.input_handler)
        self.translation_ops = TranslationOperations(translator, console, self.ui, self.input_handler)

    # File operations delegation
    def compare_srt_files(self, working_directory: str):
        """Handle SRT file comparison using git difftool."""
        self.file_ops.compare_srt_files(working_directory)

    def adjust_subtitle_timing(self, working_directory: str):
        """Handle subtitle timing adjustment with backup to .old file."""
        self.file_ops.adjust_subtitle_timing(working_directory)

    def convert_vtt_files(self, working_directory: str):
        """Handle VTT to SRT conversion."""
        self.file_ops.convert_vtt_files(working_directory)

    def organize_files(self, working_directory: str):
        """Handle file organization."""
        self.file_ops.organize_files(working_directory)

    # Translation operations delegation
    def manage_translation_cache(self):
        """Handle translation cache management."""
        self.translation_ops.manage_translation_cache()

    def translate_single_file(self, working_directory: str):
        """Handle translation of a single SRT file with proper progress tracking."""
        self.translation_ops.translate_single_file(working_directory)

    def show_available_languages(self):
        """Display available languages for translation."""
        try:
            translator_instance = self.translation_ops.translator
            available_languages = translator_instance.get_available_languages()
            default_target_language = translator_instance.get_default_target_language()

            lang_table = self.ui.show_languages_table(available_languages, default_target_language)
            self.console.print(lang_table)

        except Exception as e:
            error_message = "Error getting languages: %s" % e
            error_panel = Panel(error_message, style="red")
            self.console.print(error_panel)

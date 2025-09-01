"""Translation-related operations for the video organizer."""

from typing import List

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from nichi.constants import EXT_SRT
from nichi.core.translator import SRTTranslator
from nichi.ui.components import UIComponents
from nichi.ui.input import UserInput


class TranslationOperations:
    """Translation-related operations for file handling."""

    def __init__(
        self,
        translator: SRTTranslator,
        console: Console,
        ui: UIComponents,
        input_handler: UserInput,
    ):
        self.translator = translator
        self.console = console
        self.ui = ui
        self.input_handler = input_handler

    def get_srt_files(self, directory: str) -> List[str]:
        """Get list of SRT files in directory."""
        import os

        try:
            items = os.listdir(directory)
            srt_files = []
            for item in items:
                if item.lower().endswith(EXT_SRT):
                    srt_files.append(item)
            return srt_files
        except Exception:
            return []

    def manage_translation_cache(self):
        """Handle translation cache management."""
        try:
            # Get cache info
            cache_info = self.translator.translator.get_cache_info()

            # Show current cache status
            cache_table = self.ui.show_cache_info_table(cache_info)
            self.console.print(cache_table)

            file_count = cache_info["files"]
            if file_count == 0:
                self.console.print("[yellow]Translation cache is empty[/yellow]")
                return

            # Ask user if they want to clear cache
            clear_confirmed = self.input_handler.confirm_cache_clear(cache_info)
            if clear_confirmed:
                progress_description = "[progress.description]{task.description}"
                with Progress(
                    SpinnerColumn(),
                    TextColumn(progress_description),
                    console=self.console,
                ) as progress:
                    progress.add_task("Clearing translation cache...", total=None)

                    clear_result = self.translator.translator.clear_cache()
                    success, message, new_cache_info = clear_result

                    if success:
                        result_table = self.ui.show_cache_clear_results(message, new_cache_info)
                        self.console.print(result_table)
                        self.console.print("[green]Cache cleared successfully![/green]")
                    else:
                        self.console.print("[red]Failed to clear cache: %s[/red]" % message)
            else:
                self.console.print("[yellow]Cache clearing cancelled[/yellow]")

        except Exception as e:
            self.console.print("[red]Error managing cache: %s[/red]" % e)

    def translate_single_file(self, working_directory: str):
        """Handle translation of a single SRT file with proper progress tracking."""
        srt_files = self.get_srt_files(working_directory)
        if not srt_files:
            self.console.print("[yellow]No SRT files found in directory[/yellow]")
            return

        # Show file selection table
        file_table = self.ui.show_file_selection_table(srt_files, "Available SRT Files")
        self.console.print(file_table)

        # Get file selection
        selected_file = self.input_handler.select_file_from_list(srt_files, "SRT file")
        if not selected_file:
            return

        # Get target language
        languages = self.translator.get_available_languages()
        default_target = self.translator.get_default_target_language()
        target_lang = self.input_handler.prompt_for_language("Enter target language", languages, default_target)
        if not target_lang:
            self.console.print("[yellow]Translation cancelled[/yellow]")
            return

        # Get source language
        detected_source = self.translator.detect_source_language(selected_file)
        source_prompt = "Enter source language (or press enter for auto-detect)"
        source_lang = self.input_handler.prompt_for_language(
            source_prompt,
            languages,
            detected_source,
        )

        import os

        # Check if output exists
        expected_output = self.translator.formatter.format_output_filename(selected_file, target_lang)
        output_path = os.path.join(working_directory, expected_output)
        path_exists = os.path.exists(output_path)
        if path_exists:
            overwrite_confirmed = self.input_handler.confirm_overwrite(expected_output)
            if not overwrite_confirmed:
                self.console.print("[yellow]Translation cancelled[/yellow]")
                return

        # Perform translation with progress
        input_path = os.path.join(working_directory, selected_file)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task("Preparing translation...", total=100)

            def progress_callback(current: int, total: int):
                if total > 0:
                    ratio = current / total
                    completed = int(ratio * 100)
                    description = "Translating batch %d/%d" % (current, total)
                    progress.update(
                        task,
                        completed=completed,
                        total=100,
                        description=description,
                    )

            try:
                translation_result = self.translator.translate_file(
                    input_path,
                    target_lang,
                    source_lang,
                    progress_callback=progress_callback,
                )
                result = translation_result
                progress.update(task, completed=100, description="Translation complete")

            except Exception as error:
                progress.stop()
                self.console.print("[red]Translation failed: %s[/red]" % error)
                return

        result_table = self.ui.show_translation_results(result)
        self.console.print(result_table)
        self.console.print("[green]Translation completed successfully![/green]")

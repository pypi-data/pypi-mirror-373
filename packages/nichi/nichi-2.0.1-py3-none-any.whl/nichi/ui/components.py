"""UI components for the video organizer TUI."""

import os
from typing import Dict, List

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nichi.constants import EXT_MP4, EXT_SRT, EXT_VTT, EXT_EN_SRT
from nichi.models import TranslationResult


class UIComponents:
    """Reusable UI components for the TUI."""

    def __init__(self, console: Console):
        self.console = console

    def create_header(self, working_directory: str) -> Panel:
        """Create application header panel."""
        title_text = Text("VIDEO FILE ORGANIZER", style="bold blue")
        directory_message = "Directory: %s" % working_directory
        directory_text = Text(directory_message, style="dim")
        content = Align.left("%s\n%s" % (title_text, directory_text))
        return Panel(content, style="blue")

    def create_menu(self) -> Panel:
        """Create menu panel."""
        menu_items = [
            "[bold green]1.[/] Convert VTT files to SRT format",
            "[bold green]2.[/] Organize MP4 and subtitle files into folders",
            "[bold green]3.[/] Show current directory contents",
            "[bold green]4.[/] Change working directory",
            "[bold cyan]5.[/] Translate SRT file to another language",
            "[bold cyan]6.[/] Show available languages for translation",
            "[bold cyan]7.[/] Adjust subtitle timing",
            "[bold cyan]8.[/] Compare two Subtitle files",
            "[bold magenta]9.[/] Manage translation cache",
            "[bold magenta]10.[/] Show environment variables",
            "[bold red]11.[/] Exit",
        ]
        menu_text = "\n".join(menu_items)
        return Panel(menu_text, title="Available Actions")

    def show_directory_contents(self, working_directory: str):
        """Display current directory contents in organized tables."""
        try:
            items = os.listdir(working_directory)
            if not items:
                message = "Directory is empty"
                warning_panel = Panel(message, style="yellow")
                self.console.print(warning_panel)
                return

            # Categorize files
            video_files = []
            vtt_files = []
            srt_files = []
            folders = []

            for item in items:
                if item.lower().endswith(EXT_MP4):
                    video_files.append(item)
                elif item.lower().endswith(EXT_VTT):
                    vtt_files.append(item)
                elif item.lower().endswith(EXT_SRT):
                    srt_files.append(item)

                item_path = os.path.join(working_directory, item)
                if os.path.isdir(item_path):
                    folders.append(item)

            tables = []

            # Create tables for each file type
            if video_files:
                video_count = len(video_files)
                title_text = "MP4 Files (%d)" % video_count
                video_table = Table(title=title_text)
                video_table.add_column("Filename", style="cyan", width=50)
                sorted_videos = sorted(video_files)
                for video_file in sorted_videos:
                    video_table.add_row(video_file)
                tables.append(video_table)

            if vtt_files:
                vtt_count = len(vtt_files)
                title_text = "VTT Files (%d)" % vtt_count
                vtt_table = Table(title=title_text)
                vtt_table.add_column("Filename", style="yellow", width=50)
                sorted_vtt = sorted(vtt_files)
                for vtt_file in sorted_vtt:
                    vtt_table.add_row(vtt_file)
                tables.append(vtt_table)

            if srt_files:
                srt_count = len(srt_files)
                title_text = "SRT Files (%d)" % srt_count
                srt_table = Table(title=title_text)
                srt_table.add_column("Filename", style="green", width=50)
                sorted_srt = sorted(srt_files)
                for srt_file in sorted_srt:
                    srt_table.add_row(srt_file)
                tables.append(srt_table)

            if folders:
                folder_count = len(folders)
                title_text = "Folders (%d)" % folder_count
                folder_table = Table(title=title_text)
                folder_table.add_column("Folder Name", style="blue", width=50)
                sorted_folders = sorted(folders)
                for folder in sorted_folders:
                    folder_table.add_row(folder)
                tables.append(folder_table)

            if tables:
                columns = Columns(tables, equal=True, expand=True)
                self.console.print(columns)
            else:
                message = "No relevant files found"
                info_panel = Panel(message, style="dim")
                self.console.print(info_panel)

        except Exception as error:
            error_message = "Error reading directory: %s" % error
            error_panel = Panel(error_message, style="red")
            self.console.print(error_panel)

    def show_file_selection_table(self, files: List[str], title: str) -> Table:
        """Create a table for file selection."""
        table = Table(title=title)
        table.add_column("Index", style="cyan", width=12)
        table.add_column("Filename", style="green", width=40)

        file_enumeration = enumerate(files, 1)
        for i, filename in file_enumeration:
            index_text = str(i)
            table.add_row(index_text, filename)

        return table

    def show_languages_table(self, languages: Dict[str, str], default_lang: str) -> Table:
        """Create a table showing available languages."""
        table = Table(title="Available Languages")
        table.add_column("Code", style="cyan", width=12)
        table.add_column("Language", style="green", width=30)
        table.add_column("Default", style="yellow", width=12)

        sorted_languages = sorted(languages.items())
        for code, name in sorted_languages:
            is_default = "Yes" if code == default_lang else ""
            table.add_row(code, name, is_default)

        return table

    def show_cache_info_table(self, cache_info: dict) -> Table:
        """Create a table showing translation cache information."""
        table = Table(title="Translation Cache Information")
        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="green", width=30)

        table.add_row("Cache Directory", cache_info["cache_dir"])
        file_count = str(cache_info["files"])
        table.add_row("Cache Files", file_count)
        size_mb = cache_info["size_mb"]
        size_text = "%s MB" % size_mb
        table.add_row("Total Size", size_text)

        file_count_value = cache_info["files"]
        if file_count_value > 0:
            total_size = cache_info["size"]
            if file_count_value > 0:
                avg_size = total_size / file_count_value
            else:
                avg_size = 0
            kb_size = avg_size / 1024
            size_text = "%.1f KB" % kb_size
            table.add_row("Average File Size", size_text)

        return table

    def show_cache_clear_results(self, message: str, cache_info: dict) -> Table:
        """Create a table showing cache clear results."""
        table = Table(title="Cache Clear Results")
        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="green", width=30)

        table.add_row("Operation", "Cache Clear")
        table.add_row("Result", message)
        remaining_files = str(cache_info["files"])
        table.add_row("Remaining Files", remaining_files)
        size_mb = cache_info["size_mb"]
        size_text = "%s MB" % size_mb
        table.add_row("Remaining Size", size_text)

        return table

    def show_translation_results(self, result: TranslationResult) -> Table:
        """Create a table showing translation results."""
        table = Table(title="Translation Complete")
        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="green", width=30)

        table.add_row("Input File", result.input_file)
        table.add_row("Output File", result.output_file)
        total_entries = str(result.total_entries)
        table.add_row("Total Entries", total_entries)
        translated_entries = str(result.translated_entries)
        table.add_row("Translated Entries", translated_entries)
        table.add_row("Target Language", result.target_language)
        source_language = result.source_language
        if source_language:
            table.add_row("Source Language", source_language)

        return table

    def show_batch_translation_results(self, successful: List[dict], failed: List[tuple], target_lang: str) -> Table:
        """Create a table showing batch translation results."""
        title_text = "Batch Translation Results (Target: %s)" % target_lang
        table = Table(title=title_text)
        table.add_column("Input File", style="cyan", width=30)
        table.add_column("Output File", style="green", width=30)
        table.add_column("Status", style="yellow", width=15)
        table.add_column("Entries", style="blue", justify="right", width=10)

        # Add successful translations
        for result in successful:
            input_file = result["input"]
            output_file = result["output"]
            entry_count = str(result["entries"])
            table.add_row(input_file, output_file, "✓ Success", entry_count)

        # Add failed translations
        for input_file, error in failed:
            table.add_row(input_file, "N/A", "✗ Failed", "0")

        return table

    def show_timing_adjustment_results(
        self,
        input_file: str,
        output_file: str,
        backup_file: str,
        entries_processed: int,
        offset_ms: int,
    ) -> Table:
        """Create a table showing timing adjustment results."""
        table = Table(title="Timing Adjustment Complete")
        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="green", width=30)

        offset_seconds = offset_ms / 1000
        if offset_ms > 0:
            direction = "Forward"
        else:
            direction = "Backward"

        table.add_row("Original File", input_file)
        table.add_row("Adjusted File", output_file)
        table.add_row("Backup Created", backup_file)
        processed_count = str(entries_processed)
        table.add_row("Entries Processed", processed_count)
        abs_seconds = abs(offset_seconds)
        time_text = "%.3fs %s" % (abs_seconds, direction)
        table.add_row("Time Adjustment", time_text)
        offset_text = "%+d" % offset_ms
        table.add_row("Offset (ms)", offset_text)

        return table

    def show_conversion_results(self, converted_files: List[tuple]) -> Table:
        """Create a table showing VTT conversion results."""
        file_count = len(converted_files)
        title_text = "Conversion Results (%d files)" % file_count
        table = Table(title=title_text)
        table.add_column("Source File", style="yellow", width=30)
        table.add_column("Output File", style="green", width=30)
        table.add_column("Cues", style="cyan", justify="right", width=10)

        for filename, cue_count in converted_files:
            file_parts = os.path.splitext(filename)
            base_name = file_parts[0]
            output_name = "%s%s" % (base_name, EXT_EN_SRT)
            cue_text = str(cue_count)
            table.add_row(filename, output_name, cue_text)

        return table

    def show_organization_results(self, created_folders: List[str]) -> Table:
        """Create a table showing organization results."""
        folder_count = len(created_folders)
        title_text = "Created Folders (%d)" % folder_count
        table = Table(title=title_text)
        table.add_column("Folder Name", style="blue", width=50)

        for folder_name in created_folders:
            table.add_row(folder_name)

        return table

"""File-related operations for the video organizer."""

import os
import shutil
import subprocess
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
)

from nichi.core.converter import VTTToSRTConverter
from nichi.core.organizer import FileOrganizer
from nichi.core.timing import SRTTimingAdjuster
from nichi.ui.components import UIComponents
from nichi.ui.input import UserInput


class FileOperations:
    """File-related operations for file handling."""

    def __init__(
        self,
        converter: VTTToSRTConverter,
        organizer: FileOrganizer,
        timing_adjuster: SRTTimingAdjuster,
        console: Console,
        ui: UIComponents,
        input_handler: UserInput,
    ):
        self.converter = converter
        self.organizer = organizer
        self.timing_adjuster = timing_adjuster
        self.console = console
        self.ui = ui
        self.input_handler = input_handler

    def get_srt_files(self, directory: str) -> List[str]:
        """Get list of SRT files in directory."""
        try:
            items = os.listdir(directory)
            srt_files = []
            for item in items:
                if item.lower().endswith(".srt"):
                    srt_files.append(item)
            return srt_files
        except Exception:
            return []

    def _get_available_diff_tools(self) -> List[tuple]:
        """Get available diff tools on the system."""
        tools = []

        git_path = shutil.which("git")
        if git_path:
            tool_info = ("git", "Git difftool")
            tools.append(tool_info)

        return tools

    def _run_git_diff(self, file1_path: str, file2_path: str):
        """Run git difftool on two files."""
        try:
            cmd = [
                "git",
                "difftool",
                "--no-index",
                "--no-prompt",
                "--tool=vimdiff",
                file1_path,
                file2_path,
            ]
            subprocess.run(cmd, check=False, shell=True)
            return True
        except Exception as e:
            error_message = "Failed to run git difftool: %s" % e
            error_panel = Panel(error_message, style="red")
            self.console.print(error_panel)
            return False

    def compare_srt_files(self, working_directory: str):
        """Handle SRT file comparison using git difftool."""
        srt_files = self.get_srt_files(working_directory)
        file_count = len(srt_files)
        if file_count < 2:
            self.console.print("[yellow]Need at least 2 SRT files to compare[/yellow]")
            return

        git_available = shutil.which("git")
        if not git_available:
            self.console.print("[red]Git is not available. Please install git to use diff functionality.[/red]")
            return

        # Show file selection table only once at the beginning
        file_table = self.ui.show_file_selection_table(srt_files, "Available SRT Files")
        self.console.print(file_table)

        self.console.print("\nSelect files to compare:")
        first_file = self.input_handler.select_file_from_list(srt_files, "First file", default=1)
        second_file = self.input_handler.select_file_from_list(srt_files, "Second file", default=2)

        if not first_file or not second_file:
            return

        # Get file paths
        first_path = os.path.join(working_directory, first_file)
        second_path = os.path.join(working_directory, second_file)

        self.console.print("[bold blue]Opening diff with git difftool...[/bold blue]")

        success = self._run_git_diff(first_path, second_path)

        if not success:
            error_message = (
                "[red]Failed to run git difftool. Make sure git is properly " "configured with a diff tool.[/red]"
            )
            self.console.print(error_message)

    def adjust_subtitle_timing(self, working_directory: str):
        """Handle subtitle timing adjustment with backup to .old file."""
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

        # Get timing offset
        offset_ms = self.input_handler.prompt_for_timing_offset()
        if offset_ms is None:
            self.console.print("[yellow]Timing adjustment cancelled[/yellow]")
            return

        # Perform timing adjustment
        input_path = os.path.join(working_directory, selected_file)

        progress_description = "[progress.description]{task.description}"
        with Progress(
            SpinnerColumn(),
            TextColumn(progress_description),
            console=self.console,
        ) as progress:
            progress.add_task("Adjusting subtitle timing...", total=None)

            try:
                adjustment_result = self.timing_adjuster.adjust_srt_file_with_backup(input_path, offset_ms)
                success, message, entries_processed, backup_filename = adjustment_result

                if success:
                    # Show results
                    result_table = self.ui.show_timing_adjustment_results(
                        selected_file,
                        selected_file,  # Same filename (original is now the adjusted version)
                        backup_filename,  # Backup filename
                        entries_processed,
                        offset_ms,
                    )
                    self.console.print(result_table)

                    self.console.print("[green]Timing adjustment completed: %s[/green]" % message)
                    self.console.print("[green]Original backed up as: %s[/green]" % backup_filename)
                else:
                    self.console.print("[red]Timing adjustment failed: %s[/red]" % message)

            except Exception as error:
                progress.stop()
                self.console.print("[red]Timing adjustment failed: %s[/red]" % error)

    def convert_vtt_files(self, working_directory: str):
        """Handle VTT to SRT conversion."""
        progress_description = "[progress.description]{task.description}"
        with Progress(
            SpinnerColumn(),
            TextColumn(progress_description),
            console=self.console,
        ) as progress:
            progress.add_task("Converting VTT files...", total=None)

            try:
                converted_files = self.converter.convert_directory(working_directory)
            except Exception as error:
                self.console.print("[red]Error during conversion: %s[/red]" % error)
                return

        if not converted_files:
            self.console.print("[yellow]No VTT files found or all already converted[/yellow]")
        else:
            result_table = self.ui.show_conversion_results(converted_files)
            self.console.print(result_table)

    def organize_files(self, working_directory: str):
        """Handle file organization."""
        progress_description = "[progress.description]{task.description}"
        with Progress(
            SpinnerColumn(),
            TextColumn(progress_description),
            console=self.console,
        ) as progress:
            progress.add_task("Organizing files...", total=None)

            try:
                results = self.organizer.organize_directory(working_directory)
            except Exception as error:
                self.console.print("[red]Error during organization: %s[/red]" % error)
                return

        if not results.created_folders:
            self.console.print("[yellow]No files to organize or folders already exist[/yellow]")
        else:
            folder_table = self.ui.show_organization_results(results.created_folders)
            self.console.print(folder_table)

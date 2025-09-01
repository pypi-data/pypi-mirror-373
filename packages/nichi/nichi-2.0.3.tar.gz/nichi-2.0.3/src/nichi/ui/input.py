"""User input handling for the video organizer TUI."""

import os
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from nichi.constants import MENU_CHOICES


class UserInput:
    """Handle user input and validation."""

    def __init__(self, console: Console):
        self.console = console

    def get_menu_choice(self) -> str:
        """Get user menu choice."""
        user_choice = Prompt.ask("Enter your choice", choices=MENU_CHOICES)
        return user_choice

    def select_file_from_list(self, files: List[str], file_type: str = "file", default: int = 1) -> Optional[str]:
        """
        Let user select a file from a list.

        Args:
            files: List of filenames
            file_type: Type description for prompts
            default: Default selection index

        Returns:
            Selected filename or None if cancelled
        """
        if not files:
            message = "No %ss found in directory" % file_type
            warning_panel = Panel(message, style="yellow")
            self.console.print(warning_panel)
            return None

        try:
            prompt_text = "Select %s (1-%d)" % (file_type, len(files))
            file_index = IntPrompt.ask(prompt_text, default=default) - 1
            if file_index < 0 or file_index >= len(files):
                error_message = "Invalid file selection"
                error_panel = Panel(error_message, style="red")
                self.console.print(error_panel)
                return None
            selected_file = files[file_index]
            return selected_file
        except (ValueError, KeyboardInterrupt):
            cancel_message = "Selection cancelled"
            cancel_panel = Panel(cancel_message, style="yellow")
            self.console.print(cancel_panel)
            return None

    def prompt_for_language(
        self,
        prompt_text: str,
        available_languages: Dict[str, str],
        default_code: str = None,
    ) -> Optional[str]:
        """
        Prompt user for language selection.

        Args:
            prompt_text: Text to display in prompt
            available_languages: Dict of language codes to names
            default_code: Default language code

        Returns:
            Selected language code or None if cancelled
        """
        if default_code and default_code in available_languages:
            language_name = available_languages[default_code]
            default_display = "%s - %s" % (default_code, language_name)
        else:
            default_display = default_code

        user_input = Prompt.ask(prompt_text, default=default_display)

        if not user_input:
            return None

        stripped_input = user_input.strip()

        # Check if it's a direct code match
        lower_input = stripped_input.lower()
        if lower_input in available_languages:
            return lower_input

        # Check if it's in "code - name" format
        if " - " in stripped_input:
            split_result = stripped_input.split(" - ")
            code_part = split_result[0]
            code = code_part.strip().lower()
            if code in available_languages:
                return code

        return stripped_input

    def confirm_cache_clear(self, cache_info: dict) -> bool:
        """
        Ask user to confirm cache clearing.

        Args:
            cache_info: Dictionary with cache information

        Returns:
            True if user confirms, False otherwise
        """
        file_count = cache_info["files"]
        if file_count == 0:
            return False

        confirmation_text = "Are you sure you want to empty the cache?"
        confirmation_result = Confirm.ask(confirmation_text, default=False)
        return confirmation_result

    def confirm_batch_translation(self, file_count: int, target_lang: str) -> bool:
        """
        Ask user to confirm batch translation.

        Args:
            file_count: Number of files to translate
            target_lang: Target language code

        Returns:
            True if user confirms, False otherwise
        """
        confirmation_text = (
            "This will translate %d SRT files to %s.\n"
            "Files with existing translated versions will be skipped.\n"
            "This operation may take several minutes. Continue?"
        ) % (file_count, target_lang)

        confirmation_result = Confirm.ask(confirmation_text, default=True)
        return confirmation_result

    def prompt_for_timing_offset(self) -> Optional[int]:
        """
        Prompt user for timing offset in milliseconds.

        Returns:
            Offset in milliseconds or None if cancelled/invalid
        """
        # Show help information
        help_text = (
            "Enter timing offset in milliseconds:\n"
            "• Positive values (e.g., 1000) delay subtitles by that amount\n"
            "• Negative values (e.g., -1500) advance subtitles by that amount\n"
            "• Examples: 1000 = +1 second, -2500 = -2.5 seconds\n"
            "• Range: ±600000 ms (±10 minutes)\n"
            "• Original file will be backed up with .old extension"
        )
        help_panel = Panel(
            help_text,
            title="Timing Adjustment Help",
            style="dim",
        )
        self.console.print(help_panel)

        while True:
            try:
                user_input = Prompt.ask("Enter offset in milliseconds (or 'cancel' to abort)", default="0")

                lower_input = user_input.lower()
                cancel_commands = ["cancel", "c", "quit", "q"]
                if lower_input in cancel_commands:
                    return None

                stripped_input = user_input.strip()
                float_value = float(stripped_input)
                offset_ms = int(float_value)

                # Validate range (±10 minutes)
                max_offset = 10 * 60 * 1000  # 10 minutes in ms
                abs_offset = abs(offset_ms)
                if abs_offset > max_offset:
                    error_message = ("Offset too large. Maximum allowed: ±%d ms (±10 minutes)") % max_offset
                    error_panel = Panel(error_message, style="red")
                    self.console.print(error_panel)
                    continue

                # Confirm the adjustment
                offset_seconds = offset_ms / 1000
                if offset_ms > 0:
                    direction = "delayed"
                else:
                    direction = "advanced"

                if offset_ms == 0:
                    confirmation_text = "No timing adjustment will be made. Continue?"
                else:
                    abs_seconds = abs(offset_seconds)
                    confirmation_text = (
                        "Subtitles will be %s by %.3f seconds.\n"
                        "Original file will be backed up with .old extension. Continue?"
                    ) % (direction, abs_seconds)

                confirmation_result = Confirm.ask(confirmation_text)
                if confirmation_result:
                    return offset_ms
                else:
                    continue

            except (ValueError, TypeError):
                error_message = "Invalid input. Please enter a number (e.g., 1000, -1500)"
                error_panel = Panel(error_message, style="red")
                self.console.print(error_panel)
                continue
            except KeyboardInterrupt:
                return None

    def confirm_overwrite(self, filename: str) -> bool:
        """Ask user to confirm file overwrite."""
        prompt_text = "Output file '%s' exists. Overwrite?" % filename
        confirmation_result = Confirm.ask(prompt_text)
        return confirmation_result

    def change_directory(self, current_directory: str) -> Optional[str]:
        """
        Handle directory change with validation.

        Args:
            current_directory: Current working directory

        Returns:
            New directory path or None if cancelled/invalid
        """
        current_message = "Current: %s" % current_directory
        current_panel = Panel(current_message, style="dim")
        self.console.print(current_panel)

        new_directory = Prompt.ask("Enter new directory path", default=current_directory)

        if not new_directory or new_directory == current_directory:
            cancel_message = "Directory change cancelled"
            cancel_panel = Panel(cancel_message, style="yellow")
            self.console.print(cancel_panel)
            return None

        expanded_path = os.path.expanduser(new_directory)
        absolute_path = os.path.abspath(expanded_path)

        path_exists = os.path.exists(absolute_path)
        is_directory = os.path.isdir(absolute_path)
        if path_exists and is_directory:
            success_message = "Directory changed to: %s" % absolute_path
            success_panel = Panel(success_message, style="green")
            self.console.print(success_panel)
            return absolute_path
        else:
            error_message = "Invalid directory path"
            error_panel = Panel(error_message, style="red")
            self.console.print(error_panel)
            return None

    def confirm_exit(self) -> bool:
        """Ask user to confirm exit."""
        confirmation_result = Confirm.ask("Are you sure you want to exit?", default="y")
        return confirmation_result

    def wait_for_continue(self):
        """Wait for user to press enter."""
        Prompt.ask("Press enter to continue", default="enter")

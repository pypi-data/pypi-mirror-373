"""Main Terminal User Interface controller."""

import os
from pathlib import Path

from rich.console import Console
from rich.table import Table

from nichi.core.converter import VTTToSRTConverter
from nichi.core.organizer import FileOrganizer
from nichi.core.timing import SRTTimingAdjuster
from nichi.core.translator import SRTTranslator
from nichi.ui.components import UIComponents
from nichi.ui.input import UserInput


class ExtendedVideoOrganizerTUI:
    """Main TUI controller - simplified and modular with diff feature."""

    def __init__(self, working_directory: str):
        self.working_directory = working_directory
        self.console = Console()

        # Initialize services
        self.converter = VTTToSRTConverter()
        self.organizer = FileOrganizer()
        self.translator = SRTTranslator()
        self.timing_adjuster = SRTTimingAdjuster()

        # Initialize UI components
        self.ui = UIComponents(self.console)
        self.input_handler = UserInput(self.console)

        # Import and initialize operations here to avoid circular import
        from nichi.core.operations import Operations

        self.operations = Operations(
            self.converter,
            self.organizer,
            self.translator,
            self.timing_adjuster,
            self.console,
        )

    def show_environment_variables(self):
        """Display relevant environment variables in a table format."""
        import os

        from nichi.constants import (
            ENV_DEFAULT_TARGET_LANGUAGE,
            ENV_GEMINI_BASE_DELAY,
            ENV_GEMINI_MAX_DELAY,
            ENV_GEMINI_MAX_RETRIES,
            ENV_GEMINI_MODEL_NAME,
            ENV_GOOGLE_AI_API_KEY,
            ENV_GOOGLE_AI_PROJECT_ID,
            ENV_TRANSLATION_BATCH_SIZE,
        )

        # Create table for environment variables
        table = Table(title="Environment Variables")
        table.add_column("Variable", style="cyan", width=30)
        table.add_column("Value", style="green", width=40)

        # Define relevant environment variables from .env.example
        relevant_vars = [
            ENV_GOOGLE_AI_API_KEY,
            ENV_GEMINI_MODEL_NAME,
            ENV_GOOGLE_AI_PROJECT_ID,
            ENV_TRANSLATION_BATCH_SIZE,
            ENV_DEFAULT_TARGET_LANGUAGE,
            ENV_GEMINI_MAX_RETRIES,
            ENV_GEMINI_BASE_DELAY,
            ENV_GEMINI_MAX_DELAY,
        ]

        # Show .env file contents or environment variables
        env_vars_found = {}

        # Check for .env file
        current_dir = Path.cwd()
        cwd_env = current_dir / ".env"

        if cwd_env.exists():
            try:
                with open(cwd_env, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars_found[key] = value
            except Exception:
                pass  # Continue with environment variables if .env read fails

        # Get values from environment variables or .env file
        for var in relevant_vars:
            # Check if we found it in .env file
            if var in env_vars_found:
                value = env_vars_found[var]
            else:
                # Get from system environment
                value = os.environ.get(var, "")

            # Mask sensitive information
            if var == ENV_GOOGLE_AI_API_KEY and value:
                value = "***"
            elif var == ENV_GOOGLE_AI_API_KEY and not value:
                value = "Not set"

            table.add_row(var, value if value else "Not set")

        self.console.print(table)

    def clear_screen(self):
        """Clear the console."""
        if os.name == "nt":
            clear_command = "cls"
        else:
            clear_command = "clear"
        os.system(clear_command)

    def handle_menu_choice(self, choice: str):
        """Handle user menu selection."""
        if choice == "1":
            self.operations.convert_vtt_files(self.working_directory)
        elif choice == "2":
            self.operations.organize_files(self.working_directory)
        elif choice == "3":
            self.ui.show_directory_contents(self.working_directory)
        elif choice == "4":
            new_dir = self.input_handler.change_directory(self.working_directory)
            if new_dir:
                self.working_directory = new_dir
        elif choice == "5":
            self.operations.translate_single_file(self.working_directory)
        elif choice == "6":
            self.operations.show_available_languages()
        elif choice == "7":
            self.operations.adjust_subtitle_timing(self.working_directory)
        elif choice == "8":
            self.operations.compare_srt_files(self.working_directory)
        elif choice == "9":
            self.operations.manage_translation_cache()
        elif choice == "10":
            self.show_environment_variables()
        elif choice == "11":
            exit_confirmation = self.input_handler.confirm_exit()
            if exit_confirmation:
                success_message = "Thank you for using Video File Organizer!"
                self.console.print("[green]%s[/green]" % success_message)
                return True  # Signal to exit
            return False  # Continue running

    def run(self):
        """Main application loop."""
        while True:
            self.clear_screen()
            header_panel = self.ui.create_header(self.working_directory)
            self.console.print(header_panel)
            menu_panel = self.ui.create_menu()
            self.console.print(menu_panel)

            choice = self.input_handler.get_menu_choice()

            if choice == "11":
                exit_confirmation = self.input_handler.confirm_exit()
                if exit_confirmation:
                    success_message = "Thank you for using Video File Organizer!"
                    self.console.print("[green]%s[/green]" % success_message)
                    break
                else:
                    continue

            self.clear_screen()
            should_exit = self.handle_menu_choice(choice)

            # If handle_menu_choice returns True, it means we should exit
            if should_exit:
                break

            if choice != "11":
                self.input_handler.wait_for_continue()

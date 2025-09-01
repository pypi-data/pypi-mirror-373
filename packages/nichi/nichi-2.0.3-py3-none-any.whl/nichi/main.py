#!/usr/bin/env python3
"""
Main entry point for the Video File Organizer with Translation.
Simplified version with Google Gemini translation capabilities.
"""

import argparse
import os
import sys
from nichi import __version__
from nichi.ui.tui import ExtendedVideoOrganizerTUI


def validate_directory(directory_path: str) -> str:
    """Validate and resolve directory path."""
    expanded_path = os.path.expanduser(directory_path)
    absolute_path = os.path.abspath(expanded_path)
    wdir = absolute_path

    path_exists = os.path.exists(wdir)
    if not path_exists:
        error_message = "Error: Directory '%s' does not exist." % wdir
        print(error_message)
        sys.exit(1)

    is_directory = os.path.isdir(wdir)
    if not is_directory:
        error_message = "Error: '%s' is not a directory." % wdir
        print(error_message)
        sys.exit(1)

    return wdir


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Video File Organizer with Translation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        nichi                    # Use current directory
        nichi /path/to/videos    # Use specific directory
        nichi ~/Downloads        # Use home directory path

        Features:
        • Convert VTT files to SRT format
        • Organize MP4 and subtitle files into folders
        • Translate SRT files using Google Gemini AI
        • Support for 16+ languages

        For translation setup: https://makersuite.google.com/app/apikey
        """,
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Working directory (default: current directory)",
    )
    parser.add_argument("--version", action="version", version=f"Video File Organizer v{__version__}")

    args = parser.parse_args()
    working_directory = validate_directory(args.directory)

    try:
        start_message = "Starting Video File Organizer in: %s" % working_directory
        print(start_message)
        print("Press Ctrl+C at any time to exit.\\n")

        app = ExtendedVideoOrganizerTUI(working_directory)
        app.run()

    except KeyboardInterrupt:
        print("\\n\\nApplication closed by user. Goodbye!")
        sys.exit(0)
    except ImportError as e:
        error_message = "\\n\\nImport Error: %s" % e
        print(error_message)
        install_message = "Please install dependencies: pip install -r requirements.txt"
        print(install_message)
        sys.exit(1)
    except Exception as e:
        error_message = "\\n\\nUnexpected error: %s" % e
        print(error_message)
        sys.exit(1)


if __name__ == "__main__":
    main()

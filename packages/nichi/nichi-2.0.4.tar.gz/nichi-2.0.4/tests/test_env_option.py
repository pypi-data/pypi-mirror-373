"""Test for the TUI environment variable display functionality."""

import os
import sys
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from nichi.ui.tui import ExtendedVideoOrganizerTUI


def test_show_environment_variables():
    """Test that show_environment_variables displays the correct output."""
    # Create a mock TUI instance
    tui = ExtendedVideoOrganizerTUI(".")

    # Mock the console print method and input handler
    with patch("rich.console.Console.print") as mock_print, patch.object(tui.input_handler, "wait_for_continue"):
        tui.show_environment_variables()

    # Check that the table was printed
    assert mock_print.called
    # Get the table object that was passed to print
    table_arg = mock_print.call_args[0][0]
    assert hasattr(table_arg, "title")
    assert table_arg.title == "Environment Variables"

    print("All tests passed!")


if __name__ == "__main__":
    test_show_environment_variables()

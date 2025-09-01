"""Test suite for the services module."""

from unittest.mock import patch

from nichi.services.gemini import GeminiTranslator


@patch("nichi.services.core.genai")
def test_gemini_translator_languages(mock_genai):
    """Test Gemini translator language support."""
    # Mock the GenerativeModel to avoid API calls
    mock_genai.GenerativeModel.return_value = "mock_model"

    translator = GeminiTranslator()

    # Test language name retrieval
    assert translator.get_language_name("en") == "English"
    assert translator.get_language_name("id") == "Indonesian"
    assert translator.get_language_name("unknown") == "unknown"


if __name__ == "__main__":
    # Run the test with mocking
    test_gemini_translator_languages()
    print("Service tests passed!")

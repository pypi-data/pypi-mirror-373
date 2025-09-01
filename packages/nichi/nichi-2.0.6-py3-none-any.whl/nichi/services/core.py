"""Google Gemini translation service core functionality."""

import asyncio
import hashlib
import json
import random
from typing import List, Optional, Tuple

import google.generativeai as genai
from google.api_core.exceptions import (
    DeadlineExceeded,
    InternalServerError,
    NotFound,
    PermissionDenied,
    ResourceExhausted,
    ServiceUnavailable,
)

from nichi.config import config
from nichi.constants import (
    DEFAULT_BASE_DELAY,
    DEFAULT_BATCH_SIZE,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_MAX_DELAY,
    DEFAULT_MAX_RETRIES,
    ENV_GEMINI_BASE_DELAY,
    ENV_GEMINI_MAX_DELAY,
    ENV_GEMINI_MAX_RETRIES,
    ENV_GEMINI_MODEL_NAME,
    ENV_TRANSLATION_BATCH_SIZE,
)


class GeminiCore:
    """Core functionality for Google Gemini translator."""

    _DELIMITER = "⚡"

    def __init__(self):
        """Initialize the Gemini core with configuration."""
        # Load environment variables
        api_key = config.get_api_key()
        genai.configure(api_key=api_key)

        # Configure model with system instruction
        model_name = config.get_config_value(ENV_GEMINI_MODEL_NAME, DEFAULT_GEMINI_MODEL)

        system_instruction = (
            "You are a professional subtitle translator with expertise in multiple languages and cultural contexts. \n"
            "Your role is to provide accurate, natural, and contextually appropriate translations that preserve the original meaning, \n"
            "tone, and timing of subtitles while adapting to the linguistic conventions of the target language."
        )

        self.model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)

        # Load configuration
        self.batch_size = config.get_int_config_value(ENV_TRANSLATION_BATCH_SIZE, DEFAULT_BATCH_SIZE)
        self.max_retries = config.get_int_config_value(ENV_GEMINI_MAX_RETRIES, DEFAULT_MAX_RETRIES)
        self.base_delay = config.get_float_config_value(ENV_GEMINI_BASE_DELAY, DEFAULT_BASE_DELAY)
        self.max_delay = config.get_float_config_value(ENV_GEMINI_MAX_DELAY, DEFAULT_MAX_DELAY)
        self.max_concurrent = config.get_int_config_value("MAX_CONCURRENT_REQUESTS", 5)

    def _get_cache_key(self, texts: List[str], target_language: str, source_language: str = None) -> str:
        """Generate cache key hash from translation parameters."""
        cache_data = {
            "texts": texts,
            "target_language": target_language,
            "source_language": source_language,
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_string.encode()).hexdigest()
        return cache_hash

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Retrieve cached raw Gemini response if available."""
        from nichi.services.cache import get_cached_response

        cached_response = get_cached_response(cache_key)
        return cached_response

    def _save_cached_response(self, cache_key: str, raw_response: str) -> None:
        """Save raw Gemini response to cache."""
        from nichi.services.cache import save_cached_response

        save_cached_response(cache_key, raw_response)

    def _parse_gemini_response(self, raw_response: str, original_texts: List[str]) -> List[str]:
        """
        Parse raw Gemini response into a list of translations using the unique delimiter.
        This is much more robust than relying on numbered lists from the model's output.
        """
        if not raw_response:
            return original_texts

        # Split the response using the unique delimiter
        # The split can result in an empty string at the beginning if the response starts with the delimiter
        # We also strip leading/trailing whitespace from each part.
        split_result = raw_response.split(self._DELIMITER)
        translated_parts = []
        for part in split_result:
            stripped_part = part.strip()
            if stripped_part:
                translated_parts.append(stripped_part)

        return translated_parts

    def _get_translation_prompt(self, source_lang_str: str, target_lang_str: str, batch_text: str) -> str:
        """Generate translation prompt with language-specific instructions."""

        base_instructions = [
            "1. Maintain original tone and style",
            "2. Keep non-dialogue cues like [music] or (laughs) unchanged",
            "3. Translate idioms to natural equivalents, not literally",
            "4. Make sure gender-specific terms are translated correctly based on context (e.g., in English 'good looking' can be 'tampan' or 'cantik' in Indonesian)",
            "5. [CRITICAL] Return ONLY the translations, with each translated subtitle separated by the unique delimiter '"
            + self._DELIMITER
            + "'. Do not use numbers or any other symbols.",
            "6. [CRITICAL] Subtitle can be multi-line, YOU MUST PRESERVE LINE BREAKS, DO NOT ADD OR REMOVE DELIMITER, RESPECT THE ORIGINAL SEPARATOR!",
            "7. [CRITICAL] If there are XML tags in the subtitle, preserve them exactly",
            "8. [CRITICAL] DO NOT COMBINE LINES THATS ARE SUPPOSED TO BE SEPARATED, even if the translation makes more sense if it put in one group, RESPECT THE ORIGINAL SEPARATOR!",
            "9. [CRITICAL] Use standard Indonesian subtitle conventions: prefer 'Aku' and 'Kamu' over colloquial 'Gue' and 'Lo'",
            "10. [CRITICAL] Avoid outdated or overly formal terms like 'Bung' - use modern, natural Indonesian",
            "11. [CRITICAL] Instead of using 'Bro' for 'Dude' translation use the character if possible or just remove the word if the meaning doesn't change",
            "12. [CRITICAL] Use contemporary Indonesian that sounds natural in modern subtitles",
        ]

        instructions = "\n".join(base_instructions)
        prompt = (
            "Translate the following subtitle text from %s to %s.\n\n"
            "Instructions:\n"
            "%s\n\n"
            "Text to translate:\n"
            "%s\n"
            "%s\n"
        ) % (source_lang_str, target_lang_str, instructions, self._DELIMITER, batch_text)

        return prompt

    async def translate_batch(self, texts: List[str], target_language: str, source_language: str = None) -> List[str]:
        """Translate a batch of texts using improved prompt and parsing."""
        if not texts:
            return []

        cache_key = self._get_cache_key(texts, target_language, source_language)
        cached_response = self._get_cached_response(cache_key)

        if cached_response:
            # Parse cached response
            parsed_response = self._parse_gemini_response(cached_response, texts)
            return parsed_response

        if source_language:
            source_lang_name = self.get_language_name(source_language)
        else:
            source_lang_name = "the detected language"
        source_lang_str = source_lang_name
        target_lang_str = self.get_language_name(target_language)

        # Create the text content for the model by joining the texts with the unique delimiter
        batch_text = self._DELIMITER.join(texts)

        prompt = self._get_translation_prompt(source_lang_str, target_lang_str, batch_text)

        response = await asyncio.to_thread(self.model.generate_content, prompt)

        if not response or not response.text:
            return texts  # Return original if no response

        raw_response = response.text.strip()

        self._save_cached_response(cache_key, raw_response)

        parsed_response = self._parse_gemini_response(raw_response, texts)
        return parsed_response

    async def translate_batch_with_retry(
        self, texts: List[str], target_language: str, source_language: str = None
    ) -> Tuple[List[str], bool, Optional[str]]:
        """Translate with retry logic and detailed error handling."""
        if not texts:
            return [], True, None

        last_error_message = None

        for attempt in range(self.max_retries + 1):
            try:
                translation_result = await self.translate_batch(texts, target_language, source_language)
                result = translation_result
                return result, True, None

            except ResourceExhausted as e:
                error_string = str(e)
                last_error_message = "Rate limit exceeded: %s" % error_string
                if attempt == self.max_retries:
                    return texts, False, last_error_message

                retry_multiplier = 2**attempt
                random_offset = random.uniform(0, 1)
                delay_calculation = self.base_delay * retry_multiplier + random_offset
                delay = min(delay_calculation, self.max_delay)
                await asyncio.sleep(delay)

            except (PermissionDenied, NotFound) as e:
                error_string = str(e)
                last_error_message = error_string
                return texts, False, last_error_message

            except (InternalServerError, ServiceUnavailable, DeadlineExceeded) as e:
                error_string = str(e)
                last_error_message = error_string
                if attempt == self.max_retries:
                    return texts, False, last_error_message

                retry_multiplier = 2**attempt
                random_offset = random.uniform(0, 1)
                delay_calculation = self.base_delay * retry_multiplier + random_offset
                delay = min(delay_calculation, self.max_delay)
                await asyncio.sleep(delay)

            except Exception as e:
                error_string = str(e)
                last_error_message = error_string
                if attempt == self.max_retries:
                    return texts, False, last_error_message

                retry_multiplier = 2**attempt
                random_offset = random.uniform(0, 1)
                delay_calculation = self.base_delay * retry_multiplier + random_offset
                delay = min(delay_calculation, self.max_delay)
                await asyncio.sleep(delay)

        if last_error_message:
            error_message = last_error_message
        else:
            error_message = "Translation failed"
        return texts, False, error_message

    def get_language_name(self, code: str) -> str:
        """Get full language name from code."""
        from nichi.services.gemini import GeminiTranslator

        language_map = GeminiTranslator.LANGUAGES
        lower_code = code.lower()
        language_name = language_map.get(lower_code, code)
        return language_name

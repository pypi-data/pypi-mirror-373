"""Google Gemini translation service."""

import asyncio
from typing import Callable, List, Optional, Tuple

from nichi.services.core import GeminiCore
from nichi.services.cache import get_cache_info, clear_cache


class GeminiTranslator:
    """High-performance Google Gemini translator for subtitles."""

    LANGUAGES = {
        "en": "English",
        "id": "Indonesian",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "ar": "Arabic",
        "hi": "Hindi",
        "th": "Thai",
        "vi": "Vietnamese",
        "nl": "Dutch",
        "sv": "Swedish",
        "da": "Danish",
        "no": "Norwegian",
        "fi": "Finnish",
        "pl": "Polish",
        "tr": "Turkish",
    }

    def __init__(self):
        """Initialize the Gemini translator."""
        self.core = GeminiCore()
        # Expose core properties for backward compatibility
        self.batch_size = self.core.batch_size
        self.max_retries = self.core.max_retries
        self.max_concurrent = self.core.max_concurrent

    def get_language_name(self, code: str) -> str:
        """Get full language name from code."""
        language_name = self.LANGUAGES.get(code.lower(), code)
        return language_name

    def get_cache_info(self) -> dict:
        """Get information about cache usage."""
        cache_info = get_cache_info()
        return cache_info

    def clear_cache(self) -> Tuple[bool, str, dict]:
        """
        Clear translation cache.

        Returns:
            Tuple of (success: bool, message: str, cache_info: dict)
        """
        clear_result = clear_cache()
        return clear_result

    async def translate_batches_concurrent(
        self,
        batch_groups: List[List[str]],
        target_language: str,
        source_language: str = None,
    ) -> Tuple[List[List[str]], List[bool], List[Optional[str]]]:
        """Translate multiple batches concurrently - KEY PERFORMANCE IMPROVEMENT"""
        max_concurrent = self.core.max_concurrent
        semaphore = asyncio.Semaphore(max_concurrent)

        async def translate_single_batch_safe(texts):
            async with semaphore:
                translation_result = await self.core.translate_batch_with_retry(texts, target_language, source_language)
                return translation_result

        # Process all batches concurrently
        tasks = [translate_single_batch_safe(batch) for batch in batch_groups]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        translations = []
        success_flags = []
        error_messages = []

        for result in results:
            if isinstance(result, tuple) and len(result) == 3:
                translation, success, error_msg = result
                translations.append(translation)
                success_flags.append(success)
                error_messages.append(error_msg)
            else:
                # Fallback for unexpected results
                translations.append(batch_groups[len(translations)])
                success_flags.append(False)
                error_messages.append("Unexpected error occurred")

        return translations, success_flags, error_messages

    def translate_texts(
        self,
        texts: List[str],
        target_language: str,
        source_language: str = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[str]:
        """Translate list of texts with concurrent processing for maximum performance."""
        if not texts:
            return []

        # Split into batches
        batch_size = self.core.batch_size
        batch_count = len(texts)
        batches = [texts[i : i + batch_size] for i in range(0, batch_count, batch_size)]

        total_batches = len(batches)
        all_translations = []

        async def translate_all_batches():
            # Use concurrent processing instead of sequential
            translation_results = await self.translate_batches_concurrent(batches, target_language, source_language)
            translated_batch_results, success_flags, error_messages = translation_results

            # Process results
            batch_enumeration = zip(translated_batch_results, success_flags, error_messages)
            for batch_idx, (translated_batch, success, error_msg) in enumerate(batch_enumeration):
                if progress_callback:
                    progress_callback(batch_idx + 1, total_batches)

                all_translations.extend(translated_batch)

                # Log errors if needed (you can add error callback here)
                if not success and error_msg:
                    warning_message = "Warning: Batch %d failed: %s" % (batch_idx + 1, error_msg)
                    print(warning_message)

        asyncio.run(translate_all_batches())
        return all_translations

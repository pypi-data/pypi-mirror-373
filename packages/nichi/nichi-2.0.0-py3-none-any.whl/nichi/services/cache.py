"""Translation cache management for the video organizer."""

import json
from pathlib import Path

from nichi.constants import CONFIG_DIR, CACHE_DIR


def get_cache_directory() -> Path:
    """Get the cache directory path."""
    home_path = Path.home()
    cache_path = home_path / CONFIG_DIR / CACHE_DIR
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def get_cached_response(cache_key: str) -> str:
    """Retrieve cached raw Gemini response if available."""
    cache_dir = get_cache_directory()
    cache_filename = "%s.json" % cache_key
    cache_file = cache_dir / cache_filename
    file_exists = cache_file.exists()
    if file_exists:
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                raw_response = cached_data.get("raw_response", "")
                return raw_response
        except (json.JSONDecodeError, IOError):
            # Remove corrupted cache file
            cache_file.unlink(missing_ok=True)
    return ""


def save_cached_response(cache_key: str, raw_response: str) -> None:
    """Save raw Gemini response to cache."""
    cache_dir = get_cache_directory()
    cache_filename = "%s.json" % cache_key
    cache_file = cache_dir / cache_filename
    try:
        import asyncio

        event_loop = asyncio.get_event_loop()
        current_time = event_loop.time()
        cache_data = {
            "raw_response": raw_response,
            "timestamp": current_time,
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except IOError:
        pass  # Silently fail if cache write fails


def get_cache_info() -> dict:
    """Get information about cache usage."""
    cache_dir = get_cache_directory()

    dir_exists = cache_dir.exists()
    if not dir_exists:
        cache_dir_str = str(cache_dir)
        return {"cache_dir": cache_dir_str, "files": 0, "size": 0}

    json_files = cache_dir.glob("*.json")
    cache_files = list(json_files)
    file_stats = [f.stat().st_size for f in cache_files if f.exists()]
    total_size = sum(file_stats)

    cache_dir_str = str(cache_dir)
    file_count = len(cache_files)
    if total_size == 0:
        size_mb = 0
    else:
        mb_size = total_size / (1024 * 1024)
        size_mb = round(mb_size, 2)
    return {
        "cache_dir": cache_dir_str,
        "files": file_count,
        "size": total_size,
        "size_mb": size_mb,
    }


def clear_cache() -> tuple[bool, str, dict]:
    """
    Clear translation cache.

    Returns:
        Tuple of (success: bool, message: str, cache_info: dict)
    """
    try:
        cache_info_before = get_cache_info()

        file_count = cache_info_before["files"]
        if file_count == 0:
            return True, "Cache is already empty", cache_info_before

        # Remove all cache files
        cache_dir = get_cache_directory()
        json_files = cache_dir.glob("*.json")
        for cache_file in json_files:
            cache_file.unlink()

        cache_info_after = get_cache_info()
        cleared_count = cache_info_before["files"]
        cleared_size = cache_info_before["size_mb"]
        message = "Cleared %d cache files (%.1f MB)" % (cleared_count, cleared_size)
        return True, message, cache_info_after

    except Exception as e:
        error_string = str(e)
        error_message = "Failed to clear cache: %s" % error_string
        current_cache_info = get_cache_info()
        return False, error_message, current_cache_info

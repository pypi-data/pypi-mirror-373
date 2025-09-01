"""Test suite for the models module."""

from nichi.models import (
    SRTEntry,
    TranslationResult,
    FileProcessingResult,
    CacheInfo,
    TimingAdjustmentResult,
    Language,
    TranslationProgress,
)


def test_srt_entry():
    """Test SRT entry model."""
    entry = SRTEntry(index=1, start_time="00:00:01,500", end_time="00:00:03,000", text="Hello world!")

    assert entry.index == 1
    assert entry.start_time == "00:00:01,500"
    assert entry.end_time == "00:00:03,000"
    assert entry.text == "Hello world!"


def test_translation_result():
    """Test translation result model."""
    result = TranslationResult(
        input_file="test.srt",
        output_file="test.id.srt",
        total_entries=10,
        translated_entries=10,
        target_language="id",
        source_language="en",
    )

    assert result.input_file == "test.srt"
    assert result.output_file == "test.id.srt"
    assert result.total_entries == 10
    assert result.translated_entries == 10
    assert result.target_language == "id"
    assert result.source_language == "en"


def test_file_processing_result():
    """Test file processing result model."""
    result = FileProcessingResult(created_folders=["folder1", "folder2"], processed_files=["file1.mp4", "file1.srt"])

    assert len(result.created_folders) == 2
    assert "folder1" in result.created_folders
    assert "folder2" in result.created_folders
    assert len(result.processed_files) == 2
    assert "file1.mp4" in result.processed_files


def test_cache_info():
    """Test cache info model."""
    info = CacheInfo(cache_dir="/tmp/cache", files=5, size=10240, size_mb=0.01)

    assert info.cache_dir == "/tmp/cache"
    assert info.files == 5
    assert info.size == 10240
    assert info.size_mb == 0.01


def test_timing_adjustment_result():
    """Test timing adjustment result model."""
    result = TimingAdjustmentResult(
        input_file="test.srt", output_file="test.srt", backup_file="test.srt.old", entries_processed=10, offset_ms=1000
    )

    assert result.input_file == "test.srt"
    assert result.output_file == "test.srt"
    assert result.backup_file == "test.srt.old"
    assert result.entries_processed == 10
    assert result.offset_ms == 1000


def test_language():
    """Test language model."""
    lang = Language(code="en", name="English")

    assert lang.code == "en"
    assert lang.name == "English"


def test_translation_progress():
    """Test translation progress model."""
    progress = TranslationProgress(current_batch=2, total_batches=5, translated_entries=20, total_entries=50)

    assert progress.current_batch == 2
    assert progress.total_batches == 5
    assert progress.translated_entries == 20
    assert progress.total_entries == 50


if __name__ == "__main__":
    test_srt_entry()
    test_translation_result()
    test_file_processing_result()
    test_cache_info()
    test_timing_adjustment_result()
    test_language()
    test_translation_progress()
    print("Model tests passed!")

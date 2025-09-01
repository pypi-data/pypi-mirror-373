"""Data models for the Video File Organizer application."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SRTEntry:
    """Represents a single SRT subtitle entry."""

    index: int
    start_time: str
    end_time: str
    text: str


@dataclass
class TranslationResult:
    """Result of a translation operation."""

    input_file: str
    output_file: str
    total_entries: int
    translated_entries: int
    target_language: str
    source_language: Optional[str] = None


@dataclass
class FileProcessingResult:
    """Result of a file processing operation."""

    created_folders: list[str]
    processed_files: list[str]


@dataclass
class CacheInfo:
    """Information about the translation cache."""

    cache_dir: str
    files: int
    size: int
    size_mb: float


@dataclass
class TimingAdjustmentResult:
    """Result of a timing adjustment operation."""

    input_file: str
    output_file: str
    backup_file: str
    entries_processed: int
    offset_ms: int


@dataclass
class Language:
    """Represents a language with code and name."""

    code: str
    name: str


@dataclass
class TranslationProgress:
    """Represents progress of a translation operation."""

    current_batch: int
    total_batches: int
    translated_entries: int
    total_entries: int

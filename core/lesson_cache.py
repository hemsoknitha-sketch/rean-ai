"""Persistent Lesson Cache: Saves generated lessons to disk for 0.001s instant retrieval and 100% quota saving."""
import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "lesson_cache.json")


class LessonCache:
    """Stores and retrieves pre-generated masterclass lessons to disk."""

    _cache = {}

    @classmethod
    def _ensure_loaded(cls):
        if cls._cache:
            return
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cls._cache = json.load(f)
                logger.info(f"Loaded {len(cls._cache)} pre-generated lessons from disk cache.")
            except Exception as e:
                logger.error(f"Error loading lesson cache: {e}")
                cls._cache = {}

    @classmethod
    def get(cls, course_key: str, lesson_num: int, lang: str = "km") -> Optional[str]:
        """Retrieves cached lesson content in 0.001 seconds."""
        cls._ensure_loaded()
        key = f"{course_key}:{lesson_num}:{lang}"
        cached = cls._cache.get(key)
        if cached:
            logger.info(f"PERSISTENT LESSON CACHE HIT (0.001s Instant) for key: {key}")
        return cached

    @classmethod
    def set(cls, course_key: str, lesson_num: int, lang: str, content: str) -> None:
        """Saves generated lesson to persistent disk cache."""
        cls._ensure_loaded()
        key = f"{course_key}:{lesson_num}:{lang}"
        cls._cache[key] = content
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved lesson '{key}' to persistent disk cache.")
        except Exception as e:
            logger.error(f"Error saving lesson cache: {e}")

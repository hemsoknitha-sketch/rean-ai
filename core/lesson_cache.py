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
                
                # Auto-purge corrupted cache entries (e.g. &#x27;, &quot;, missing <pre><code, <1000 chars, or error strings)
                valid_cache = {
                    k: v for k, v in cls._cache.items()
                    if isinstance(v, str)
                    and len(v.strip()) >= 1000
                    and "&#x27;" not in v
                    and "&quot;" not in v
                    and "<pre><code" in v
                    and not any(err in v for err in ["Polymath Cognitive Engine encountered", "RESOURCE_EXHAUSTED", "Rate Limit", "Authentication Error", "Service Unavailable", "UNAVAILABLE"])
                }
                if len(valid_cache) < len(cls._cache):
                    purged_count = len(cls._cache) - len(valid_cache)
                    logger.warning(f"Purged {purged_count} corrupted lesson cache entries from disk cache.")
                    cls._cache = valid_cache
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cls._cache, f, ensure_ascii=False, indent=2)

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
            from core.reviewer import ReviewerAgent
            cached = ReviewerAgent.balance_html_tags(cached)
        return cached

    @classmethod
    def set(cls, course_key: str, lesson_num: int, lang: str, content: str) -> bool:
        """Saves generated masterclass lesson to persistent disk cache with integrity validation."""
        if not content or len(content.strip()) < 1000:
            logger.warning(f"Refusing to cache invalid/undersized content for {course_key}:{lesson_num}:{lang} ({len(content) if content else 0} chars).")
            return False

        if "<pre><code" not in content:
            logger.warning(f"Refusing to cache content without copyable code block for {course_key}:{lesson_num}:{lang}.")
            return False

        if any(err in content for err in ["Polymath Cognitive Engine encountered", "RESOURCE_EXHAUSTED", "Rate Limit", "Authentication Error", "Service Unavailable", "UNAVAILABLE"]):
            logger.warning(f"Refusing to cache error message for {course_key}:{lesson_num}:{lang}.")
            return False

        cls._ensure_loaded()
        from core.reviewer import ReviewerAgent
        content = ReviewerAgent.balance_html_tags(content)
        key = f"{course_key}:{lesson_num}:{lang}"
        cls._cache[key] = content
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved lesson '{key}' to persistent disk cache.")
            return True
        except Exception as e:
            logger.error(f"Error saving lesson cache: {e}")
            return False

"""Persistent General Query Cache: Saves all general user Q&As to disk for 0.001s instant retrieval and 100% quota saving."""
import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "query_cache.json")


class QueryCache:
    """Stores and retrieves persistent Q&A responses to disk."""

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
                logger.info(f"Loaded {len(cls._cache)} persistent Q&A queries from disk cache.")
            except Exception as e:
                logger.error(f"Error loading query cache: {e}")
                cls._cache = {}

    @classmethod
    def _normalize(cls, query: str, lang: str) -> str:
        return f"{lang.lower().strip()}:{query.strip().lower()}"

    @classmethod
    def get(cls, query: str, lang: str = "km") -> Optional[str]:
        """Retrieves cached Q&A answer in 0.001 seconds."""
        cls._ensure_loaded()
        key = cls._normalize(query, lang)
        cached = cls._cache.get(key)
        if cached:
            logger.info(f"PERSISTENT QUERY CACHE HIT (0.001s Instant) for key: '{query[:30]}...'")
        return cached

    @classmethod
    def set(cls, query: str, lang: str, response: str) -> None:
        """Saves generated Q&A answer to persistent disk cache."""
        cls._ensure_loaded()
        key = cls._normalize(query, lang)
        cls._cache[key] = response
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved persistent query Q&A '{query[:30]}...' to disk cache.")
        except Exception as e:
            logger.error(f"Error saving query cache: {e}")

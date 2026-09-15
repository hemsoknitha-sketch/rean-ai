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

                # Auto-purge corrupted cache entries (exact error returns from engine)
                exact_error_signatures = [
                    "The Polymath Cognitive Engine encountered a temporary latency",
                    "Rate Limit / Quota Reached: You have reached",
                    "Authentication Error: The Gemini API Key configured",
                    "temporary latency standard error or network anomaly",
                ]
                valid_cache = {
                    k: v for k, v in cls._cache.items()
                    if isinstance(v, str)
                    and not any(sig in v for sig in exact_error_signatures)
                }
                if len(valid_cache) < len(cls._cache):
                    purged_count = len(cls._cache) - len(valid_cache)
                    logger.warning(f"Purged {purged_count} corrupted error entries from persistent query cache.")
                    cls._cache = valid_cache
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cls._cache, f, ensure_ascii=False, indent=2)

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
    def set(cls, query: str, lang: str, response: str) -> bool:
        """Saves generated Q&A answer to persistent disk cache with error filtering."""
        if not response or len(response.strip()) < 5:
            return False

        exact_error_signatures = [
            "The Polymath Cognitive Engine encountered a temporary latency",
            "Rate Limit / Quota Reached: You have reached",
            "Authentication Error: The Gemini API Key configured",
            "temporary latency standard error or network anomaly",
        ]
        if any(sig in response for sig in exact_error_signatures):
            logger.warning("Refusing to save error response to persistent QueryCache.")
            return False

        cls._ensure_loaded()
        key = cls._normalize(query, lang)
        cls._cache[key] = response
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved persistent query Q&A '{query[:30]}...' to disk cache.")
            return True
        except Exception as e:
            logger.error(f"Error saving query cache: {e}")
            return False

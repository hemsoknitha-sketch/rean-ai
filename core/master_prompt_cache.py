"""Persistent Disk Cache Engine for /master_prompt (0.001s Instant Load + $0 API Cost)."""
import os
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "master_prompt_cache.json")


class MasterPromptCache:
    """Manages persistent disk caching for generated Master Prompts."""
    
    _cache: Dict[str, str] = {}

    @classmethod
    def _load_cache(cls) -> None:
        """Loads cache from disk if available."""
        if not cls._cache and os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cls._cache = json.load(f)
                logger.info(f"Loaded {len(cls._cache)} entries from Master Prompt Disk Cache.")
            except Exception as e:
                logger.error(f"Failed to load Master Prompt cache: {e}")
                cls._cache = {}

    @classmethod
    def _save_cache(cls) -> None:
        """Saves in-memory cache to disk JSON."""
        try:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save Master Prompt cache to disk: {e}")

    @classmethod
    def _normalize(cls, raw_prompt: str) -> str:
        return raw_prompt.strip().lower()

    @classmethod
    def get(cls, raw_prompt: str) -> Optional[str]:
        cls._load_cache()
        key = cls._normalize(raw_prompt)
        cached_result = cls._cache.get(key)
        if cached_result:
            logger.info(f"MASTER PROMPT CACHE HIT (0.001s response) for: '{raw_prompt[:30]}...'")
        return cached_result

    @classmethod
    def set(cls, raw_prompt: str, generated_master_prompt: str) -> None:
        cls._load_cache()
        key = cls._normalize(raw_prompt)
        cls._cache[key] = generated_master_prompt
        cls._save_cache()

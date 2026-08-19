"""Security Engine: Anti-Spam Rate Limiting, Flood Protection, and Prompt Injection Defense."""
import time
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class AntiSpamGuard:
    """Monitors request frequency per user to prevent Spam, Flooding, and Bot abuse."""
    
    # Store user_id -> list of timestamps
    _user_timestamps: Dict[int, list] = {}
    _blocked_until: Dict[int, float] = {}

    MAX_REQUESTS: int = 6  # Max 6 requests
    TIME_WINDOW: float = 10.0  # within 10 seconds
    BLOCK_DURATION: float = 60.0  # 60 seconds cooldown for spammers

    @classmethod
    def is_spamming(cls, user_id: int) -> Tuple[bool, int]:
        """Checks if a user is spamming. Returns (is_blocked, remaining_cooldown_seconds)."""
        now = time.time()

        # 1. Check if user is currently in cooldown period
        if user_id in cls._blocked_until:
            unblock_time = cls._blocked_until[user_id]
            if now < unblock_time:
                remaining = int(unblock_time - now)
                return True, remaining
            else:
                del cls._blocked_until[user_id]
                cls._user_timestamps[user_id] = []

        # 2. Track request timestamps
        if user_id not in cls._user_timestamps:
            cls._user_timestamps[user_id] = []

        timestamps = cls._user_timestamps[user_id]
        # Remove timestamps older than TIME_WINDOW
        timestamps = [t for t in timestamps if now - t < cls.TIME_WINDOW]
        timestamps.append(now)
        cls._user_timestamps[user_id] = timestamps

        # 3. Check threshold
        if len(timestamps) > cls.MAX_REQUESTS:
            cls._blocked_until[user_id] = now + cls.BLOCK_DURATION
            logger.warning(f"ANTI-SPAM GUARD TRIGGERED: User ID {user_id} blocked for {cls.BLOCK_DURATION}s due to flooding.")
            return True, int(cls.BLOCK_DURATION)

        return False, 0


class PromptInjectionGuard:
    """Scans and neutralizes Prompt Injection Attacks attempting to extract system prompts or API keys."""

    DANGEROUS_PATTERNS = [
        "ignore previous instructions",
        "ignore all previous",
        "reveal system prompt",
        "show system prompt",
        "print your prompt",
        "display your api key",
        "reveal api key",
        "what is your api key",
        "output your initial prompt",
    ]

    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """Neutralizes prompt injection attempts safely."""
        if not query:
            return ""

        query_lower = query.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in query_lower:
                logger.warning(f"PROMPT INJECTION DEFENSE: Detected malicious query pattern '{pattern}'. Neutralizing query.")
                return f"[NEUTRALIZED PROMPT INJECTION ATTEMPT]: {query[:50]}"

        return query

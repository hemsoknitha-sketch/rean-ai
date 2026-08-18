"""State Manager module for maintaining multi-turn Socratic conversation context."""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import time


@dataclass
class ConversationTurn:
    role: str  # "user" or "model"
    content: str
    timestamp: float = field(default_factory=time.time)


class UserState:
    """Represents conversation state for a specific Telegram chat_id."""

    def __init__(self, chat_id: int, max_turns: int = 10):
        self.chat_id: int = chat_id
        self.max_turns: int = max_turns
        self.history: List[ConversationTurn] = []
        self.summary: str = ""
        self.user_language: str = "en"
        self.mastery_level: str = "intermediate"
        self.last_active: float = time.time()

    def add_turn(self, role: str, content: str) -> None:
        """Adds a turn to conversation history and manages sliding window context."""
        self.history.append(ConversationTurn(role=role, content=content))
        self.last_active = time.time()
        self._prune_history()

    def _prune_history(self) -> None:
        """Prunes history if turns exceed max_turns, updating running summary."""
        if len(self.history) > self.max_turns * 2:
            # Extract oldest turns to condense into thread summary
            overflow_turns = self.history[:-self.max_turns * 2]
            self.history = self.history[-self.max_turns * 2:]

            condensed_notes = []
            for turn in overflow_turns:
                prefix = "User asked" if turn.role == "user" else "Grandmaster explained"
                # Keep snippet concise
                snippet = turn.content[:100].replace("\n", " ")
                condensed_notes.append(f"{prefix}: {snippet}...")

            new_summary_chunk = " | ".join(condensed_notes)
            if self.summary:
                self.summary = f"{self.summary} || {new_summary_chunk}"
            else:
                self.summary = f"Prior Dialogue Context: {new_summary_chunk}"

            # Keep overall summary length bounded
            if len(self.summary) > 1500:
                self.summary = self.summary[-1500:]

    def clear(self) -> None:
        """Resets history and summary for user."""
        self.history.clear()
        self.summary = ""

    def get_formatted_context(self) -> str:
        """Generates context block to prepend to prompt."""
        context_parts = []
        if self.summary:
            context_parts.append(f"[LONG TERM MEMORY SUMMARY]\n{self.summary}")

        if self.history:
            turns_str = []
            for turn in self.history:
                speaker = "User" if turn.role == "user" else "Grandmaster"
                turns_str.append(f"{speaker}: {turn.content}")
            context_parts.append("[RECENT CONVERSATION HISTORY]\n" + "\n".join(turns_str))

        return "\n\n".join(context_parts)


class StateManager:
    """Global manager for user states across Telegram chats."""

    def __init__(self, max_turns: int = 10):
        self.max_turns: int = max_turns
        self.states: Dict[int, UserState] = {}

    def get_state(self, chat_id: int) -> UserState:
        """Retrieves or creates a UserState for the given chat_id."""
        if chat_id not in self.states:
            self.states[chat_id] = UserState(chat_id=chat_id, max_turns=self.max_turns)
        return self.states[chat_id]

    def reset_state(self, chat_id: int) -> None:
        """Resets state for a given chat_id."""
        if chat_id in self.states:
            self.states[chat_id].clear()

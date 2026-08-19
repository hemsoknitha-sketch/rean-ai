"""Novel Continuity Engine & Khmer Romance Lexicon RAM Memory.

Manages multi-chapter narrative continuity, character state tracking, Heat Level preservation (1-5),
and RAM-cached authentic Khmer romantic vocabulary.
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

CONTINUITY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "novel_continuity.json")


class KhmerRomanceLexicon:
    """RAM Memory Lexicon containing rich Khmer romantic, emotional, and sensual expressions."""

    SKIN_LEVEL_TERMS = [
        "ស្បែកសខ្ចីម៉ដ្ឋខៃដូចបណ្តូលចេក", "សម្បុរស្រស់ថ្លាដូចដំណក់សន្សើម", "រោចញើសស្រាលៗលើស្បែកទន់ល្មៃ",
        "ព្រឺសម្បុរខ្ញាកៗពេញផ្ទៃខ្នង", "ដង្ហើមភាយកម្ដៅក្តៅឧណ្ហៗ", "ចង្វាក់បេះដូងលោតញាប់រន្ធត់",
        "បបូរមាត់ក្រហមព្រឿងៗញ័រទទ្រើក", "សរសៃសក់ខ្មៅរលោងធ្លាក់គ្របស្មា", "កែវភ្នែកភ្លឺថ្លាញ័ររន្ធត់ដោយក្តីរំភើប"
    ]

    HEAT_LEVEL_TERMS = [
        "រលកកម្ដៅនៃតណ្ហាបក់បោក", "រស្មីស្នេហាក្តៅរោលរាលពេញរាងកាយ", "ភាពទន់ជ្រាយនិងក្តីស្រើបស្រាល",
        "ក្តីអាឡោះអាឡ័យជម្រៅបេះដូង", "រំញោចរំភើបជ្រួតជ្រាបដល់សរសៃប្រសាទ", "អារម្មណ៍ស្ទើរស្ទុះហោះហើរលើអាកាស"
    ]

    LITERARY_CONNECTORS = [
        "ប្រទាក់ក្រឡាគ្នាយ៉ាងស្អិតល្មួត", "បន្តរឿងរ៉ាវពីជំពូកមុនដោយគ្មានចន្លោះ", "ទាក់ទាញអារម្មណ៍យ៉ាងជ្រាលជ្រៅ",
        "ឆ្លុះបញ្ចាំងពីក្តីស្នេហ៍ដ៏បរិសុទ្ធនិងក្តៅរោលរាល", "គ្មានការច្រឡំតួអង្គឬរំលងសកម្មភាពឡើយ"
    ]

    @classmethod
    def get_lexicon_prompt_injection(cls) -> str:
        """Injects RAM Lexicon vocabulary instructions into system prompts."""
        skin_str = ", ".join(cls.SKIN_LEVEL_TERMS[:5])
        heat_str = ", ".join(cls.HEAT_LEVEL_TERMS[:5])
        return (
            f"KHMER ROMANCE LEXICON (RAM MEMORY INTEGRATED):\n"
            f"• Sensory Vocabulary: {skin_str}\n"
            f"• Emotional & Heat Terms: {heat_str}\n"
            f"• Adhere strictly to Samdech Sangha Raja Chuon Nath Khmer Dictionary prose."
        )


class NovelContinuityTracker:
    """Tracks active novel plot arcs, character states, and multi-chapter progress per user."""

    _user_novels: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _load(cls) -> None:
        if cls._user_novels:
            return
        if os.path.exists(CONTINUITY_FILE):
            try:
                with open(CONTINUITY_FILE, "r", encoding="utf-8") as f:
                    cls._user_novels = json.load(f)
                logger.info(f"Loaded {len(cls._user_novels)} active novel continuity states.")
            except Exception as e:
                logger.error(f"Error loading novel continuity DB: {e}")
                cls._user_novels = {}

    @classmethod
    def _save(cls) -> None:
        try:
            os.makedirs(os.path.dirname(CONTINUITY_FILE), exist_ok=True)
            with open(CONTINUITY_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._user_novels, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving novel continuity DB: {e}")

    @classmethod
    def update_novel_state(
        cls,
        user_id: int,
        heat_level: int,
        characters: str,
        chapter_num: int,
        chapter_content: str
    ) -> None:
        """Saves current chapter context and updates novel state for seamless chapter N+1 continuity."""
        cls._load()
        user_key = str(user_id)

        if user_key not in cls._user_novels:
            cls._user_novels[user_key] = {
                "heat_level": heat_level,
                "characters": characters,
                "chapters": {},
                "last_chapter_num": 0
            }

        # Store last 300 chars of current chapter as summary context for next chapter
        summary_snippet = chapter_content[-400:].strip() if len(chapter_content) > 400 else chapter_content
        cls._user_novels[user_key]["chapters"][str(chapter_num)] = summary_snippet
        cls._user_novels[user_key]["last_chapter_num"] = chapter_num
        cls._user_novels[user_key]["heat_level"] = heat_level
        if characters:
            cls._user_novels[user_key]["characters"] = characters

        cls._save()

    @classmethod
    def get_novel_context(cls, user_id: int, target_chapter: int) -> str:
        """Retrieves previous chapter context and character state for target chapter."""
        cls._load()
        user_key = str(user_id)
        if user_key not in cls._user_novels:
            return ""

        novel_data = cls._user_novels[user_key]
        last_num = novel_data.get("last_chapter_num", 0)
        prev_chapter_summary = novel_data.get("chapters", {}).get(str(last_num), "")

        if prev_chapter_summary:
            return (
                f"\n\nCONTINUITY CONTEXT FROM PREVIOUS CHAPTER (Chapter {last_num}):\n"
                f"Previous Chapter Ending Context:\n\"{prev_chapter_summary}\"\n"
                f"Instructions for Chapter {target_chapter}:\n"
                f"• Seamlessly continue the storyline directly from Chapter {last_num} without skipping events or resetting character relationships.\n"
                f"• Maintain exact character identities ({novel_data.get('characters', '')}) and maintain Heat Level {novel_data.get('heat_level', 4)} strictly."
            )
        return ""

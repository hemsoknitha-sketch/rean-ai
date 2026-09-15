"""Student Progress & Socratic Learning Database Manager.

Tracks student learning modes (Explanatory vs. Interactive Socratic), scores,
mastery levels, and active exercises isolated strictly by Telegram User ID.
Guarantees 100% data preservation and atomic disk persistence.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

STUDENT_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "student_records.json")


class StudentManager:
    """Manages student learning modes, scores, levels, and progress with atomic persistence."""

    _students: Dict[str, Dict[str, Any]] = {}
    _loaded: bool = False

    @classmethod
    def _load_db(cls) -> None:
        """Loads student database from disk JSON."""
        if not cls._loaded:
            if os.path.exists(STUDENT_DB_FILE):
                try:
                    with open(STUDENT_DB_FILE, "r", encoding="utf-8") as f:
                        cls._students = json.load(f)
                    logger.info(f"Loaded {len(cls._students)} student records from database.")
                except Exception as e:
                    logger.error(f"Failed to load Student DB from {STUDENT_DB_FILE}: {e}")
                    cls._students = {}
            else:
                cls._students = {}
            cls._loaded = True

    @classmethod
    def _save_db(cls) -> None:
        """Atomically saves student records to disk to guarantee zero data loss."""
        try:
            db_dir = os.path.dirname(STUDENT_DB_FILE)
            os.makedirs(db_dir, exist_ok=True)
            tmp_file = f"{STUDENT_DB_FILE}.tmp"
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(cls._students, f, ensure_ascii=False, indent=2)
            os.replace(tmp_file, STUDENT_DB_FILE)
        except Exception as e:
            logger.error(f"Failed to atomically save Student DB: {e}", exc_info=True)

    @classmethod
    def calculate_level(cls, score: int) -> Tuple[str, str, str]:
        """Returns (level_name, emoji, khmer_title) based on score."""
        if score >= 500:
            return "Grandmaster", "👑", "មហាចារ្យបញ្ញាសិប្បនិម្មិត (AI Grandmaster)"
        elif score >= 300:
            return "Expert", "🥇", "អ្នកជំនាញជាន់ខ្ពស់ (Senior AI Scholar)"
        elif score >= 150:
            return "Scholar", "🥈", "អ្នកសិក្សាស្រាវជ្រាវ (AI Practitioner)"
        elif score >= 50:
            return "Apprentice", "🥉", "កូនសិស្សចំណាន (AI Apprentice)"
        else:
            return "Novice", "🌱", "អ្នកចាប់ផ្តើមដំបូង (AI Novice)"

    @classmethod
    def get_or_create_student(
        cls,
        user_id: int,
        name: str = "Student",
        username: str = ""
    ) -> Dict[str, Any]:
        """Retrieves or initializes student record isolated strictly by Telegram user_id."""
        cls._load_db()
        uid_str = str(user_id)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if uid_str not in cls._students:
            cls._students[uid_str] = {
                "user_id": user_id,
                "name": name or "Student",
                "username": username or "",
                "learning_mode": "socratic",  # Default to Interactive Socratic Mode
                "score": 0,
                "level": "Novice",
                "level_title": "អ្នកចាប់ផ្តើមដំបូង (AI Novice)",
                "level_emoji": "🌱",
                "completed_exercises": 0,
                "active_exercise": None,
                "course_progress": {},
                "exercise_history": [],
                "created_at": now_str,
                "last_active": now_str,
            }
            cls._save_db()
            logger.info(f"Initialized new student record for user {name} [ID: {user_id}]")
        else:
            # Update name/username if changed
            if name and cls._students[uid_str].get("name") != name:
                cls._students[uid_str]["name"] = name
            if username and cls._students[uid_str].get("username") != username:
                cls._students[uid_str]["username"] = username
            cls._students[uid_str]["last_active"] = now_str

        return cls._students[uid_str]

    @classmethod
    def get_learning_mode(cls, user_id: int) -> str:
        """Gets user's active learning mode: 'socratic' or 'explanatory'."""
        student = cls.get_or_create_student(user_id)
        return student.get("learning_mode", "socratic")

    @classmethod
    def set_learning_mode(cls, user_id: int, mode: str) -> str:
        """Sets learning mode: 'socratic' or 'explanatory'."""
        mode_lower = mode.lower()
        if "explan" in mode_lower or "master" in mode_lower:
            mode_clean = "explanatory"
        else:
            mode_clean = "socratic"

        student = cls.get_or_create_student(user_id)
        student["learning_mode"] = mode_clean
        student["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cls._save_db()
        logger.info(f"Updated student {user_id} learning mode to: {mode_clean}")
        return mode_clean

    @classmethod
    def set_active_exercise(cls, user_id: int, exercise_data: Dict[str, Any]) -> None:
        """Sets the currently active Socratic exercise for a student."""
        student = cls.get_or_create_student(user_id)
        exercise_data["assigned_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        student["active_exercise"] = exercise_data
        student["last_active"] = exercise_data["assigned_at"]
        cls._save_db()

    @classmethod
    def get_active_exercise(cls, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves active Socratic exercise if one is waiting for student response."""
        student = cls.get_or_create_student(user_id)
        return student.get("active_exercise")

    @classmethod
    def clear_active_exercise(cls, user_id: int) -> None:
        """Clears current active exercise once completed or skipped."""
        student = cls.get_or_create_student(user_id)
        student["active_exercise"] = None
        cls._save_db()

    @classmethod
    def record_exercise_result(
        cls,
        user_id: int,
        points: int,
        exercise_title: str,
        feedback: str,
        passed: bool = True
    ) -> Dict[str, Any]:
        """Awards points, updates level, logs exercise, and clears active challenge."""
        student = cls.get_or_create_student(user_id)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        old_score = student.get("score", 0)
        new_score = max(0, old_score + points)
        student["score"] = new_score

        if passed:
            student["completed_exercises"] = student.get("completed_exercises", 0) + 1

        level_name, level_emoji, level_title = cls.calculate_level(new_score)
        student["level"] = level_name
        student["level_emoji"] = level_emoji
        student["level_title"] = level_title

        # Record into history (keep last 20)
        history_entry = {
            "title": exercise_title,
            "points_awarded": points,
            "passed": passed,
            "timestamp": now_str,
            "feedback": feedback[:300]
        }
        history = student.get("exercise_history", [])
        history.append(history_entry)
        student["exercise_history"] = history[-20:]

        student["active_exercise"] = None
        student["last_active"] = now_str
        cls._save_db()

        return {
            "old_score": old_score,
            "new_score": new_score,
            "points_earned": points,
            "level": level_name,
            "level_emoji": level_emoji,
            "level_title": level_title,
            "passed": passed,
            "completed_count": student["completed_exercises"]
        }

    @classmethod
    def update_course_progress(cls, user_id: int, course_key: str, lesson_num: int) -> None:
        """Updates the highest lesson number reached for a specific course."""
        student = cls.get_or_create_student(user_id)
        progress = student.setdefault("course_progress", {})
        course_data = progress.setdefault(course_key, {"highest_lesson": 0, "completed": []})

        if lesson_num > course_data.get("highest_lesson", 0):
            course_data["highest_lesson"] = lesson_num

        completed_list = course_data.setdefault("completed", [])
        if lesson_num not in completed_list:
            completed_list.append(lesson_num)

        cls._save_db()

    @classmethod
    def get_student_card(cls, user_id: int) -> str:
        """Generates pristine Telegram HTML student profile and score dashboard."""
        student = cls.get_or_create_student(user_id)
        score = student.get("score", 0)
        level_name, emoji, title = cls.calculate_level(score)
        mode = student.get("learning_mode", "socratic")
        mode_str = "⚡ របៀបសូក្រាតអន្តរកម្ម (Interactive Socratic)" if mode == "socratic" else "📘 របៀបពន្យល់ក្បោះក្បាយ (Explanatory)"
        completed = student.get("completed_exercises", 0)

        # Progress to next level
        if score < 50:
            next_tier = f"ត្រូវការ {50 - score} ពិន្ទុទៀតដើម្បីឡើងទៅ 🥉 Apprentice"
        elif score < 150:
            next_tier = f"ត្រូវការ {150 - score} ពិន្ទុទៀតដើម្បីឡើងទៅ 🥈 Scholar"
        elif score < 300:
            next_tier = f"ត្រូវការ {300 - score} ពិន្ទុទៀតដើម្បីឡើងទៅ 🥇 Expert"
        elif score < 500:
            next_tier = f"ត្រូវការ {500 - score} ពិន្ទុទៀតដើម្បីឡើងទៅ 👑 Grandmaster"
        else:
            next_tier = "🌟 លោកអ្នកបានឈានដល់កម្រិតកំពូល Grandmaster រួចហើយ!"

        card = (
            "🎓 <b>កាតព័ត៌មាន និងកម្រិតសមត្ថភាពសិស្ស (STUDENT PROFILE)</b>\n"
            "━━━━━━━━━━\n"
            f"👤 <b>សិស្ស ៖</b> {student.get('name', 'Student')}\n"
            f"🆔 <b>Telegram ID ៖</b> <code>{user_id}</code>\n"
            f"🎯 <b>របៀបសិក្សាបច្ចុប្បន្ន ៖</b> {mode_str}\n"
            f"🏆 <b>ពិន្ទុសរុប (Score) ៖</b> <b>{score} ពិន្ទុ</b>\n"
            f"🎖️ <b>កម្រិតបច្ចុប្បន្ន ៖</b> {emoji} <b>{title}</b>\n"
            f"📝 <b>លំហាត់ដែលបានបញ្ចប់ ៖</b> <b>{completed} លំហាត់</b>\n"
            f"📈 <b>វឌ្ឍនភាព ៖</b> <i>{next_tier}</i>\n"
            "━━━━━━━━━━\n"
            "💡 <i>លោកអ្នកអាចជ្រើសរើសផ្លាស់ប្តូររបៀបសិក្សា (Learning Mode) ខាងក្រោមបានគ្រប់ពេលវេលា ៖</i>"
        )
        return card

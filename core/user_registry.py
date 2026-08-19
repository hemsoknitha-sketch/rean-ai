"""User Registry Engine: Tracks registered bot users and identifies non-VIP/Free leads."""
import os
import json
import time
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime

from core.vip_manager import VIPManager

logger = logging.getLogger(__name__)

USER_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "registered_users.json")


class UserRegistry:
    """Manages persistent registration of all bot users and free lead tracking."""
    
    _users: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _load_db(cls) -> None:
        """Loads user database from JSON file."""
        if not cls._users and os.path.exists(USER_DB_FILE):
            try:
                with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                    cls._users = json.load(f)
                logger.info(f"Loaded {len(cls._users)} users from User Registry DB.")
            except Exception as e:
                logger.error(f"Failed to load User Registry DB: {e}")
                cls._users = {}

    @classmethod
    def _save_db(cls) -> None:
        """Saves user database to disk JSON."""
        try:
            os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
            with open(USER_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save User Registry DB: {e}")

    @classmethod
    def register_user(cls, user) -> Tuple[bool, Dict[str, Any]]:
        """
        Registers a user on /start. 
        Returns (is_new_user, user_info).
        """
        cls._load_db()
        user_id_str = str(user.id)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user_id_str in cls._users:
            # Update existing info
            cls._users[user_id_str]["name"] = user.first_name or "User"
            if user.username:
                cls._users[user_id_str]["username"] = user.username
            cls._save_db()
            return False, cls._users[user_id_str]

        # New User Registration
        user_info = {
            "id": user.id,
            "name": user.first_name or "User",
            "username": user.username or "",
            "joined_at": now_str
        }
        cls._users[user_id_str] = user_info
        cls._save_db()
        logger.info(f"Registered NEW user: {user.first_name} [ID: {user.id}]")
        return True, user_info

    @classmethod
    def get_free_users(cls) -> List[Dict[str, Any]]:
        """Returns list of users who have tapped /start but are NOT currently VIP/Super VIP."""
        cls._load_db()
        free_users = []
        for user_id_str, info in cls._users.items():
            user_id = int(user_id_str)
            if not VIPManager.is_vip(user_id):
                free_users.append(info)
        # Sort by joined_at descending (newest leads first)
        free_users.sort(key=lambda x: x.get("joined_at", ""), reverse=True)
        return free_users

"""VIP License Security Manager: Persistent VIP User Authorization with Expiration Tracking."""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

VIP_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "vip_users.json")


class VIPManager:
    """Manages VIP licenses, subscription validity, and access enforcement."""

    _vips: Dict[str, Dict] = {}

    @classmethod
    def _ensure_loaded(cls):
        if cls._vips:
            return
        os.makedirs(os.path.dirname(VIP_FILE), exist_ok=True)
        if os.path.exists(VIP_FILE):
            try:
                with open(VIP_FILE, "r", encoding="utf-8") as f:
                    cls._vips = json.load(f)
                logger.info(f"Loaded {len(cls._vips)} VIP user licenses from disk.")
            except Exception as e:
                logger.error(f"Error loading VIP database: {e}")
                cls._vips = {}

    @classmethod
    def save(cls):
        try:
            with open(VIP_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._vips, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving VIP database: {e}")

    @classmethod
    def is_vip(cls, user_id: int, admin_id: int = 859271875) -> bool:
        """Checks if user is Super Admin OR has an active, unexpired VIP license."""
        # Super Admin always has full lifetime VIP access
        if user_id == admin_id or user_id == 859271875:
            return True

        cls._ensure_loaded()
        uid_str = str(user_id)
        info = cls._vips.get(uid_str)
        if not info:
            return False

        # Lifetime subscription check
        if info.get("is_lifetime", False):
            return True

        # Check expiration date
        expiry_str = info.get("expiry_date")
        if not expiry_str:
            return False

        try:
            expiry_dt = datetime.fromisoformat(expiry_str)
            return datetime.now() < expiry_dt
        except Exception:
            return False

    @classmethod
    def is_super_vip(cls, user_id: int, admin_id: int = 859271875) -> bool:
        """Checks if user is Super Admin OR has an active SUPER_VIP license."""
        if user_id == admin_id or user_id == 859271875:
            return True

        if not cls.is_vip(user_id, admin_id):
            return False

        cls._ensure_loaded()
        info = cls._vips.get(str(user_id), {})
        return info.get("tier") == "SUPER_VIP"

    @classmethod
    def add_vip(cls, user_id: int, name: str = "VIP User", days: int = 30, tier: str = "VIP", is_lifetime: bool = False) -> str:
        """Grants or extends VIP or SUPER_VIP access for a user."""
        cls._ensure_loaded()
        uid_str = str(user_id)
        now = datetime.now()

        if is_lifetime or days <= 0:
            expiry_str = "LIFETIME"
            expiry_display = "Lifetime Unlimited"
        else:
            if cls.is_vip(user_id):
                curr_info = cls._vips.get(uid_str, {})
                curr_expiry = curr_info.get("expiry_date")
                if curr_expiry and curr_expiry != "LIFETIME":
                    try:
                        base_dt = datetime.fromisoformat(curr_expiry)
                        if base_dt > now:
                            now = base_dt
                    except Exception:
                        pass
            expiry_dt = now + timedelta(days=days)
            expiry_str = expiry_dt.isoformat()
            expiry_display = expiry_dt.strftime("%Y-%m-%d %H:%M:%S")

        cls._vips[uid_str] = {
            "user_id": user_id,
            "name": name,
            "tier": "SUPER_VIP" if tier.upper() == "SUPER_VIP" else "VIP",
            "added_date": datetime.now().isoformat(),
            "expiry_date": expiry_str,
            "is_lifetime": is_lifetime or (expiry_str == "LIFETIME"),
            "days_granted": days
        }
        cls.save()
        logger.info(f"Granted {tier} to user {user_id} ({name}) until {expiry_display}.")
        return expiry_display

    @classmethod
    def revoke_vip(cls, user_id: int) -> bool:
        """Revokes VIP or Super VIP access for a user."""
        cls._ensure_loaded()
        uid_str = str(user_id)
        if uid_str in cls._vips:
            del cls._vips[uid_str]
            cls.save()
            return True
        return False

    @classmethod
    def get_vip_info(cls, user_id: int) -> Optional[Dict]:
        """Gets VIP subscription details for a user."""
        cls._ensure_loaded()
        uid_str = str(user_id)
        info = cls._vips.get(uid_str)
        if not info:
            return None

        tier_label = info.get("tier", "VIP")

        if info.get("is_lifetime"):
            info["status"] = f"ACTIVE ({tier_label} Lifetime)"
            info["remaining_days"] = "Unlimited"
            info["tier"] = tier_label
            return info

        expiry_str = info.get("expiry_date")
        if not expiry_str:
            info["status"] = "EXPIRED"
            info["remaining_days"] = 0
            info["tier"] = tier_label
            return info

        try:
            expiry_dt = datetime.fromisoformat(expiry_str)
            now = datetime.now()
            if now < expiry_dt:
                diff = expiry_dt - now
                info["status"] = f"ACTIVE ({tier_label})"
                info["remaining_days"] = diff.days
            else:
                info["status"] = "EXPIRED"
                info["remaining_days"] = 0
        except Exception:
            info["status"] = "UNKNOWN"
            info["remaining_days"] = 0

        info["tier"] = tier_label
        return info

    @classmethod
    def list_all_vips(cls) -> List[Dict]:
        """Lists all registered VIP and Super VIP users with current subscription status."""
        cls._ensure_loaded()
        result = []
        for uid, info in cls._vips.items():
            parsed = cls.get_vip_info(int(uid))
            if parsed:
                result.append(parsed)
        return result


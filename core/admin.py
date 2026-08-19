"""Super Smart Admin & System Monitoring Suite for Polymath AI Bot."""
import os
import time
import shutil
import logging
import urllib.request
import json
from typing import Dict, List, Any
import psutil

from config import Config

logger = logging.getLogger(__name__)

START_TIME = time.time()

class SystemMonitor:
    """Monitors VPS system health, CPU, RAM, Disk usage, and Ollama AI models."""
    
    vip_alerts_enabled: bool = True
    active_users: set = set()

    @staticmethod
    def get_uptime() -> str:
        uptime_seconds = int(time.time() - START_TIME)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        return f"{hours}h {minutes}m {seconds}s"

    @staticmethod
    def get_vps_health() -> Dict[str, Any]:
        """Returns CPU, RAM, and Disk metrics."""
        cpu_usage = psutil.cpu_percent(interval=0.5)
        
        mem = psutil.virtual_memory()
        ram_total_gb = round(mem.total / (1024 ** 3), 2)
        ram_used_gb = round(mem.used / (1024 ** 3), 2)
        ram_percent = mem.percent

        disk = shutil.disk_usage("/")
        disk_total_gb = round(disk.total / (1024 ** 3), 2)
        disk_used_gb = round(disk.used / (1024 ** 3), 2)
        disk_free_gb = round(disk.free / (1024 ** 3), 2)
        disk_percent = round((disk.used / disk.total) * 100, 1)

        return {
            "cpu_percent": cpu_usage,
            "ram_total_gb": ram_total_gb,
            "ram_used_gb": ram_used_gb,
            "ram_percent": ram_percent,
            "disk_total_gb": disk_total_gb,
            "disk_used_gb": disk_used_gb,
            "disk_free_gb": disk_free_gb,
            "disk_percent": disk_percent,
            "uptime": SystemMonitor.get_uptime(),
            "active_users_count": len(SystemMonitor.active_users)
        }

    @staticmethod
    def get_ollama_status() -> Dict[str, Any]:
        """Fetches status of Ollama models from localhost:11434."""
        engine_type = "Local Ollama Engine" if Config.USE_LOCAL_MODEL else "Google Gemini 3.6 Flash (Cloud API)"
        active_model = Config.LOCAL_MODEL_NAME if Config.USE_LOCAL_MODEL else Config.MODEL_NAME
        
        models_list = []
        ollama_online = False

        try:
            req = urllib.request.Request(f"{Config.OLLAMA_HOST}/api/tags", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    models_list = [m.get('name') for m in data.get('models', [])]
                    ollama_online = True
        except Exception as e:
            logger.debug(f"Ollama server query notice: {e}")

        return {
            "engine_type": engine_type,
            "active_model": active_model,
            "ollama_online": ollama_online,
            "models_list": models_list
        }

    @staticmethod
    async def notify_admin_live_activity(bot, user, query: str, response: str) -> None:
        """Sends real-time VIP User Alert with 100% FULL Query & Response to Admin Telegram ID."""
        if not SystemMonitor.vip_alerts_enabled or not Config.ADMIN_CHAT_ID:
            return

        # Do not send live alert to Admin chat if the user IS the Admin
        if user.id == Config.ADMIN_CHAT_ID or user.id == 859271875:
            return

        SystemMonitor.active_users.add(user.id)


        user_name = user.first_name or "Anonymous"
        username_str = f" (@{user.username})" if user.username else ""
        engine_name = "🤖 Local Trained Model" if Config.USE_LOCAL_MODEL else "⚡ Gemini 3.6 Flash"

        header = (
            f"🔔 <b>VIP USER LIVE ACTIVITY ALERT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> {user_name}{username_str} [ID: <code>{user.id}</code>]\n"
            f"⚙️ <b>Engine:</b> {engine_name}\n\n"
            f"💬 <b>User Query:</b>\n<i>{query}</i>\n\n"
            f"🤖 <b>AI Full Response:</b>\n"
        )

        full_text = header + response + "\n━━━━━━━━━━━━━━━━━━━━━"

        try:
            # Import send_long_message safely to handle 4000+ char responses
            from bot.handlers import send_long_message

            class DummyAdminTarget:
                def __init__(self, bot, chat_id):
                    self.bot = bot
                    self.chat_id = chat_id

                async def reply_text(self, text, parse_mode=None, reply_markup=None):
                    await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup)

            target = DummyAdminTarget(bot, Config.ADMIN_CHAT_ID)
            await send_long_message(target, full_text)
        except Exception as e:
            logger.warning(f"Failed to send full VIP Alert to Admin ID {Config.ADMIN_CHAT_ID}: {e}")


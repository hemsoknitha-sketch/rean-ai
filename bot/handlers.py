"""Telegram Bot Command and Message Handlers with Interactive AI Course, 100-Lesson Curriculum Engine, & Super Admin Suite."""
import html as py_html
import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import Config
from memory.state_manager import StateManager
from core.evaluator import EvaluatorAgent
from core.architect import ArchitectAgent
from core.reviewer import ReviewerAgent
from core.curriculum import CurriculumEngine, AI_COURSES
from core.admin import SystemMonitor
from core.lesson_cache import LessonCache
from core.vip_manager import VIPManager
from core.novel_cache import NovelCache
from core.novel_18_cache import Novel18Cache
from core.master_prompt_cache import MasterPromptCache
from core.security import AntiSpamGuard, PromptInjectionGuard
from core.user_registry import UserRegistry
from core.backup_engine import BackupEngine
from core.novel_continuity import NovelContinuityTracker, KhmerRomanceLexicon
from core.student_manager import StudentManager






logger = logging.getLogger(__name__)




# Initialize cognitive components
state_manager = StateManager(max_turns=Config.MAX_MEMORY_TURNS)
evaluator_agent = EvaluatorAgent()
architect_agent = ArchitectAgent()
reviewer_agent = ReviewerAgent()


def is_admin(user_id: int) -> bool:
    """Checks if the user ID matches Config.ADMIN_CHAT_ID or 859271875."""
    return user_id == Config.ADMIN_CHAT_ID or user_id == 859271875


async def check_vip_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Enforces VIP authorization. Returns True if authorized, False if blocked."""
    user = update.effective_user
    if not user:
        return False

    if VIPManager.is_vip(user.id):
        return True

    text = (
        "🔒 <b>ការកម្រិតសិទ្ធិ ៖ ទាមទារអាជ្ញាប័ណ្ណ VIP MEMBERSHIP</b>\n"
        "━━━━━━━━━━\n"
        "ដើម្បីចូលរៀនមេរៀន AI Masterclasses ទាំង ៧០០ មេរៀន និងប្រើប្រាស់ AI Cognitive Engine សូមធ្វើការដំឡើងគណនីរបស់លោកអ្នកទៅជា <b>VIP Membership</b>។\n\n"
        f"👤 <b>ឈ្មោះ ៖</b> {user.first_name}\n"
        f"🆔 <b>លេខ Telegram ID របស់លោកអ្នក ៖</b> <code>{user.id}</code>\n\n"
        "📩 <b>ទំនាក់ទំនងដើម្បីជាវ ឬបើកសិទ្ធិអាជ្ញាប័ណ្ណ VIP ៖</b>\n"
        "សូមផ្ញើលេខ Telegram ID ខាងលើទៅកាន់ Admin ដើម្បីបើកសិទ្ធិប្រើប្រាស់ ៖\n"
        "• <b>Telegram Admin ៖</b> <b>@Sokpheatonsai</b>\n"
        "━━━━━━━━━━"
    )


    if update.callback_query:
        await update.callback_query.message.reply_text(text, parse_mode=ParseMode.HTML)
    elif update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    return False



async def send_long_message(target_msg, text: str, reply_markup=None) -> None:
    """Splits long text into clean atomic chunks and ensures bulletproof HTML rendering with zero broken tags."""
    max_len = 4050

    def heal_chunk(raw_html: str) -> str:
        """Heals common HTML parsing pitfalls and balances tags for Telegram Bot API."""
        h = (
            raw_html.replace("&#x27;", "'")
            .replace("&#39;", "'")
            .replace("&apos;", "'")
            .replace("&quot;", '"')
        )
        allowed_tags = {
            "b", "strong", "i", "em", "u", "ins", "s", "strike", "del",
            "span", "tg-spoiler", "a", "code", "pre", "blockquote", "tg-emoji"
        }
        def replace_unsupported_tag(m):
            tag_name = m.group(1).lower()
            if tag_name in allowed_tags:
                return m.group(0)
            return m.group(0).replace("<", "&lt;").replace(">", "&gt;")

        sanitized = re.sub(r"</?([a-zA-Z0-9_\-]+)(?:\s+[^>]*)?>", replace_unsupported_tag, h)
        return ReviewerAgent.balance_html_tags(sanitized)

    async def safe_reply(chunk: str, reply_markup=None, markup=None):
        effective_markup = reply_markup if reply_markup is not None else markup
        healed_chunk = heal_chunk(chunk)
        try:
            await target_msg.reply_text(healed_chunk, parse_mode=ParseMode.HTML, reply_markup=effective_markup)
        except Exception as html_err:
            logger.warning(f"Telegram HTML parse failed: {html_err}. Attempting plain-text fallback.")
            clean_plain = py_html.unescape(re.sub(r"<[^>]+>", "", chunk))
            await target_msg.reply_text(clean_plain, reply_markup=effective_markup)

    if len(text) <= max_len:
        await safe_reply(text, reply_markup=reply_markup)
        return

    # Atomic Unit Splitting: Never split inside <pre><code ...>...</code></pre> blocks
    code_block_pattern = re.compile(r"(<pre><code.*?>.*?</code></pre>)", re.DOTALL)
    parts = code_block_pattern.split(text)

    atomic_units = []
    for part in parts:
        if not part:
            continue
        if part.startswith("<pre><code") and part.endswith("</code></pre>"):
            atomic_units.append(part)
        else:
            paragraphs = part.split("\n\n")
            for p in paragraphs:
                if p.strip():
                    atomic_units.append(p)

    chunks = []
    current_chunk = []
    current_length = 0

    for unit in atomic_units:
        unit_len = len(unit) + 2
        if len(unit) > max_len:
            lines = unit.split("\n")
            for line in lines:
                if current_length + len(line) + 1 > max_len:
                    if current_chunk:
                        chunks.append("\n\n".join(current_chunk))
                    current_chunk = [line]
                    current_length = len(line)
                else:
                    current_chunk.append(line)
                    current_length += len(line) + 1
        elif current_length + unit_len > max_len:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [unit]
            current_length = len(unit)
        else:
            current_chunk.append(unit)
            current_length += unit_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    for i, chunk in enumerate(chunks):
        is_last = (i == len(chunks) - 1)
        m_markup = reply_markup if is_last else None
        await safe_reply(chunk, reply_markup=m_markup)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start command with a trilingual Polymath Grandmaster greeting."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    state_manager.reset_state(chat_id)
    SystemMonitor.active_users.add(chat_id)

    # 1. Register User in Database & check if first time registration
    is_new_user, user_info = UserRegistry.register_user(user)

    # 2. Send Real-time Admin Alert on First Time Registration
    if is_new_user and Config.ADMIN_CHAT_ID and user.id != Config.ADMIN_CHAT_ID:
        try:
            username_str = f" (@{user.username})" if user.username else ""
            alert_text = (
                "🎉 <b>NEW USER REGISTERED ALERT</b>\n"
                "━━━━━━━━━━\n"
                f"👤 <b>ឈ្មោះ ៖</b> {user.first_name}{username_str}\n"
                f"🆔 <b>Telegram ID ៖</b> <code>{user.id}</code>\n"
                f"📅 <b>កាលបរិច្ឆេទ ៖</b> <code>{user_info.get('joined_at', '')}</code>\n"
                "👑 <b>ស្ថានភាព ៖</b> 🔴 មិនទាន់ជាវ VIP (Standard Lead)\n"
                "━━━━━━━━━━\n"
                f"💡 <i>Admin អាចប្រើបញ្ជា <code>/addvip {user.id} 30 {user.first_name}</code> ដើម្បីបើកសិទ្ធិ VIP!</i>"
            )
            await context.bot.send_message(chat_id=Config.ADMIN_CHAT_ID, text=alert_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.warning(f"Failed to send new user alert to admin: {e}")

    is_user_vip = VIPManager.is_vip(user.id)
    vip_info = VIPManager.get_vip_info(user.id)

    
    if is_user_vip:
        tier_str = vip_info.get('tier', 'SUPER_VIP') if vip_info else "SUPER_VIP / Admin"
        remaining_days = vip_info.get("remaining_days", "Unlimited") if vip_info else "Lifetime"
        vip_status_str = f"🟢 ACTIVE ({tier_str} - {remaining_days})"
    else:
        vip_status_str = "🔴 គណនីស្តង់ដារ (Standard Account) - ទាមទារអាជ្ញាប័ណ្ណ VIP ដើម្បីចូលរៀន"

    greeting = (
        f"✨ <b>ស្វាគមន៍មកកាន់ SUPREME POLYMATH AI GRANDMASTER!</b>\n"
        "━━━━━━━━━━\n"
        f"👋 ជម្រាបសួរ <b>{user.first_name}</b>!\n"
        "ខ្ញុំគឺជាបណ្តាញខួរក្បាលសិប្បនិម្មិត <b>Polymath AI Grandmaster</b> ដែលមានសមត្ថភាពខ្ពស់បំផុតក្នុងការបង្រៀន AI Masterclasses ទាំង ១,២០០ មេរៀន (១២ ជំនាញ AI) និងនិពន្ធប្រលោមលោកខ្មែរគ្រប់កម្រិត!\n\n"
        f"🆔 <b>លេខ Telegram ID របស់លោកអ្នក ៖</b> <code>{user.id}</code>\n"
        f"👑 <b>ស្ថានភាពអាជ្ញាប័ណ្ណ ៖</b> {vip_status_str}\n\n"
        "🌟 <b>កញ្ចប់សេវាកម្មអាជ្ញាប័ណ្ណ (MEMBERSHIP TIERS) ៖</b>\n\n"
        "១. <b>👑 VIP MEMBERSHIP (អាជ្ញាប័ណ្ណ VIP) ៖</b>\n"
        "• ចូលរៀនមេរៀន AI Masterclasses ទាំង ១,២០០ មេរៀន (១០០ មេរៀនក្នុង ១ ប្រធានបទ AI ទាំង ១២)\n"
        "• សួរសំណួរទូទៅ និងដោះស្រាយលំហាត់ល្បឿនលឿន <b>ក្រោម ១ វិនាទី (Instant Cognitive Response)</b>\n\n"

        "២. <b>🌟 SUPER VIP MEMBERSHIP (អាជ្ញាប័ណ្ណ Super VIP) ៖</b>\n"
        "• ទទួលបានអត្ថប្រយោជន៍ VIP ទាំងអស់ ១០០%\n"
        "• 📖 បើកសិទ្ធិប្រើប្រាស់ម៉ាស៊ីននិពន្ធប្រលោមលោកខ្មែរ <b>/novel_kh</b> (APEX Khmer Novelist Engine)\n"
        "• 💡 បើកសិទ្ធិប្រើប្រាស់ម៉ាស៊ីនបង្កើត Master Prompts <b>/master_prompt</b> (AGI Genesis Engine)\n"
        "• ទទួលបានសិទ្ធិអាទិភាពខ្ពស់បំផុត (Priority Processing) គ្មានថ្ងៃទើរ Quota ឡើយ!\n\n"
        "📩 <b>ទាក់ទងជាវ ឬបើកសិទ្ធិអាជ្ញាប័ណ្ណ ៖</b>\n"
        f"សូមផ្ញើលេខ Telegram ID <code>{user.id}</code> ទៅកាន់ Admin ៖\n"
        "• <b>Telegram Admin ៖</b> <b>@Sokpheatonsai</b>\n"
        "━━━━━━━━━━"
    )

    if is_admin(user.id):
        greeting += "\n\n👑 <b>Super Admin Dashboard Authorized:</b> បញ្ជា /admin សម្រាប់គ្រប់គ្រងប្រព័ន្ធ។"


    keyboard = []
    for key, info in AI_COURSES.items():
        keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['title']}", callback_data=f"course:{key}:1")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(greeting, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def ai_courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /ai or /courses command to display interactive AI learning menu."""
    if not await check_vip_access(update, context):
        return

    text = (
        "<b>🎓 បញ្ជី AI Master Courses (១០០ មេរៀន / 100 Lessons in 1 AI Topic)</b>\n\n"
        "សូមជ្រើសរើសជំនាញ AI ដែលលោកអ្នកចង់រៀនសូត្រពីកម្រិតដំបូង រហូតដល់កម្រិត Grandmaster ៖"
    )
    keyboard = []
    for key, info in AI_COURSES.items():
        keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['title']}", callback_data=f"course:{key}:1")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def study_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /study or /socratic command to view student profile, score, and select learning mode."""
    user = update.effective_user
    if not user:
        return

    # Guarantee student record exists and update activity
    StudentManager.get_or_create_student(user.id, name=user.first_name or "Student", username=user.username or "")
    card_html = StudentManager.get_student_card(user.id)

    keyboard = [
        [
            InlineKeyboardButton("⚡ របៀបសូក្រាតអន្តរកម្ម (Socratic)", callback_data="study_mode:socratic"),
            InlineKeyboardButton("📘 របៀបពន្យល់ក្បោះក្បាយ (Explanatory)", callback_data="study_mode:explanatory"),
        ],
        [
            InlineKeyboardButton("🎓 បើកមើល AI Courses (/ai)", callback_data="courses_list"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(card_html, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        except Exception:
            await update.callback_query.message.reply_text(card_html, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    else:
        await update.message.reply_text(card_html, parse_mode=ParseMode.HTML, reply_markup=reply_markup)




async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /admin command for Super Admin Control Panel."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied: Only Super Admin ID 859271875 can execute this command.</i>", parse_mode=ParseMode.HTML)
        return

    text = (
        "👑 <b>SUPER ADMIN CONTROL PANEL</b>\n"
        "━━━━━━━━━━\n"
        f"<b>Admin ID:</b> <code>{user.id}</code>\n"
        f"<b>VIP Alerts:</b> {'🟢 ENABLED' if SystemMonitor.vip_alerts_enabled else '🔴 DISABLED'}\n"
        f"<b>Active Engine:</b> {'🤖 Local Model' if Config.USE_LOCAL_MODEL else '⚡ Gemini 3.6 Flash'}\n"
        "━━━━━━━━━━\n"
        "Select an Admin control tool from the menu below:"
    )

    keyboard = [
        [
            InlineKeyboardButton("📊 VPS System Health", callback_data="admin:status"),
            InlineKeyboardButton("🤖 AI Models Status", callback_data="admin:models")
        ],
        [
            InlineKeyboardButton(f"🔔 Toggle VIP Alerts ({'ON' if SystemMonitor.vip_alerts_enabled else 'OFF'})", callback_data="admin:toggle_vip"),
            InlineKeyboardButton("🧹 Flush Cache", callback_data="admin:clearcache")
        ],
        [
            InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="admin:refresh")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /status command to display detailed VPS CPU, RAM, and Disk metrics."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    health = SystemMonitor.get_vps_health()
    text = (
        "📊 <b>VPS SYSTEM HEALTH & BOT SERVICE STATUS</b>\n"
        "━━━━━━━━━━\n"
        f"⚙️ <b>Service Status:</b> 🟢 ACTIVE (running)\n"
        f"⏱️ <b>Bot Uptime:</b> {health['uptime']}\n"
        f"💻 <b>CPU Usage:</b> {health['cpu_percent']}%\n"
        f"🧠 <b>RAM Memory:</b> {health['ram_used_gb']} GB / {health['ram_total_gb']} GB ({health['ram_percent']}%)\n"
        f"💾 <b>Disk Storage:</b> {health['disk_used_gb']} GB / {health['disk_total_gb']} GB (Free: {health['disk_free_gb']} GB - {health['disk_percent']}%)\n"
        f"👥 <b>Active Users Count:</b> {health['active_users_count']}\n"
        "━━━━━━━━━━"
    )
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /models command to view active AI model & Ollama status."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    status = SystemMonitor.get_ollama_status()
    models_str = "\n".join([f"  • <code>{m}</code>" for m in status['models_list']]) if status['models_list'] else "  <i>No models installed or server offline</i>"

    text = (
        "🤖 <b>AI MODEL ENGINE STATUS</b>\n"
        "━━━━━━━━━━\n"
        f"⚡ <b>Active Provider:</b> {status['engine_type']}\n"
        f"🎯 <b>Current Model:</b> <code>{status['active_model']}</code>\n"
        f"🌐 <b>Ollama Server (11434):</b> {'🟢 ONLINE' if status['ollama_online'] else '🔴 OFFLINE'}\n\n"
        f"<b>Installed Ollama Models:</b>\n{models_str}\n"
        "━━━━━━━━━━"
    )
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def vip_toggle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /vip command to toggle VIP Live User Activity Alerts."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    SystemMonitor.vip_alerts_enabled = not SystemMonitor.vip_alerts_enabled
    status_str = "🟢 ENABLED" if SystemMonitor.vip_alerts_enabled else "🔴 DISABLED"
    text = f"🔔 <b>VIP User Live Activity Alerts</b> are now {status_str}."

    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def clearcache_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /clearcache command to flush Architect response cache."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    architect_agent.cache.cache.clear()
    text = "🧹 <b>Response Cache Flushed!</b> Instant memory cache cleared successfully."
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)



async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /broadcast <message> to announce to all active users."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    if not context.args:
        text = (
            "📢 <b>BROADCAST ANNOUNCEMENT TOOL</b>\n"
            "━━━━━━━━━━\n"
            "To send a broadcast announcement to all active users, please type:\n\n"
            "<code>/broadcast Your Announcement Text Here</code>\n\n"
            "<i>Example:</i> <code>/broadcast 🚀 New AI Course Lessons are now available! Click /ai to learn.</code>\n"
            "━━━━━━━━━━"
        )
        if update.callback_query:
            await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    broadcast_msg = " ".join(context.args)
    count = 0
    for uid in list(SystemMonitor.active_users):
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>ANNOUNCEMENT:</b>\n\n{broadcast_msg}", parse_mode=ParseMode.HTML)
            count += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Broadcast sent successfully to {count} active users.", parse_mode=ParseMode.HTML)


async def addvip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /addvip <user_id> [days] [name] to grant or extend VIP access."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    if not context.args:
        text = (
            "👑 <b>GRANT VIP LICENSE TOOL</b>\n"
            "━━━━━━━━━━\n"
            "To grant or extend VIP access to a user, type:\n\n"
            "<code>/addvip [user_id] [days] [name]</code>\n\n"
            "<i>Examples:</i>\n"
            "• <code>/addvip 123456789 30</code> (Grants 30 days VIP access)\n"
            "• <code>/addvip 123456789 365 VIP Student</code> (Grants 1 year VIP access)\n"
            "• <code>/addvip 123456789 0 Lifetime Admin</code> (Grants Lifetime access)\n"
            "━━━━━━━━━━"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    try:
        target_id = int(context.args[0])
        days = int(context.args[1]) if len(context.args) > 1 else 30
        name = " ".join(context.args[2:]) if len(context.args) > 2 else "VIP User"
        is_lifetime = (days <= 0)

        expiry_display = VIPManager.add_vip(target_id, name=name, days=days, tier="VIP", is_lifetime=is_lifetime)
        await update.message.reply_text(
            f"✅ <b>VIP License Granted Successfully!</b>\n\n"
            f"👤 <b>User:</b> {name}\n"
            f"🆔 <b>Telegram ID:</b> <code>{target_id}</code>\n"
            f"⏳ <b>Days Granted:</b> {'LIFETIME' if is_lifetime else f'{days} days'}\n"
            f"📅 <b>Expires On:</b> <code>{expiry_display}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ <b>Error:</b> Invalid parameters ({e}).", parse_mode=ParseMode.HTML)


async def addsupervip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /addsupervip [user_id] [days] [name] to grant Super VIP tier."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    if not context.args:
        text = (
            "🌟 <b>GRANT SUPER VIP LICENSE TOOL</b>\n"
            "━━━━━━━━━━\n"
            "To grant or extend SUPER VIP tier to a user, type:\n\n"
            "<code>/addsupervip [user_id] [days] [name]</code>\n\n"
            "<i>Examples:</i>\n"
            "• <code>/addsupervip 123456789 30</code> (Grants 30 days Super VIP)\n"
            "• <code>/addsupervip 123456789 365 Super VIP Pro</code> (Grants 1 year Super VIP)\n"
            "• <code>/addsupervip 123456789 0 Lifetime Elite</code> (Grants Lifetime Super VIP)\n"
            "━━━━━━━━━━"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    try:
        target_id = int(context.args[0])
        days = int(context.args[1]) if len(context.args) > 1 else 30
        name = " ".join(context.args[2:]) if len(context.args) > 2 else "Super VIP User"
        is_lifetime = (days <= 0)

        expiry_display = VIPManager.add_vip(target_id, name=name, days=days, tier="SUPER_VIP", is_lifetime=is_lifetime)
        await update.message.reply_text(
            f"🌟 <b>SUPER VIP License Granted Successfully!</b>\n\n"
            f"👤 <b>User:</b> {name}\n"
            f"🆔 <b>Telegram ID:</b> <code>{target_id}</code>\n"
            f"👑 <b>Tier:</b> 🌟 SUPER VIP\n"
            f"⏳ <b>Days Granted:</b> {'LIFETIME' if is_lifetime else f'{days} days'}\n"
            f"📅 <b>Expires On:</b> <code>{expiry_display}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ <b>Error:</b> Invalid parameters ({e}).", parse_mode=ParseMode.HTML)



async def delvip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /delvip [user_id] to revoke VIP access."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    if not context.args:
        await update.message.reply_text("⚠️ <b>Usage:</b> <code>/delvip [user_id]</code>", parse_mode=ParseMode.HTML)
        return


    try:
        target_id = int(context.args[0])
        revoked = VIPManager.revoke_vip(target_id)
        if revoked:
            await update.message.reply_text(f"🗑️ <b>VIP License Revoked</b> for Telegram ID <code>{target_id}</code>.", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"⚠️ Telegram ID <code>{target_id}</code> was not found in VIP database.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}", parse_mode=ParseMode.HTML)



async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /backup command to trigger instant system database ZIP backup sent to Admin."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied: Only Super Admin ID 859271875 can execute this command.</i>", parse_mode=ParseMode.HTML)
        return

    msg = await update.message.reply_text("📦 <b>កំពុងបង្កើត ZIP Backup នៃ Database ទាំងអស់...</b>", parse_mode=ParseMode.HTML)
    success = await BackupEngine.send_backup_to_admin(context.bot)
    if success:
        await msg.edit_text("✅ <b>ឯកសារ Backup ZIP ត្រូវបានផ្ញើចូលទៅប្រអប់ Chat របស់ Admin រួចរាល់!</b>", parse_mode=ParseMode.HTML)
    else:
        await msg.edit_text("⚠️ កើតមានបញ្ហាក្នុងការផ្ញើ Backup File។", parse_mode=ParseMode.HTML)



async def viplist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /viplist to list all active VIP subscriptions."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    vips = VIPManager.list_all_vips()
    if not vips:
        await update.message.reply_text("📋 <b>VIP LICENSED USERS DATABASE</b>\n\n<i>No VIP users currently registered.</i>", parse_mode=ParseMode.HTML)
        return

    lines = []
    for v in vips:
        status_emoji = "🟢" if v.get('status', '').startswith("ACTIVE") else "🔴"
        lines.append(
            f"{status_emoji} <b>{v.get('name', 'VIP User')}</b> (<code>{v['user_id']}</code>)\n"
            f"   • Status: <b>{v.get('status')}</b> | Days Left: <b>{v.get('remaining_days')}</b> | Expiry: <code>{v.get('expiry_date')}</code>"
        )

    text = "📋 <b>VIP LICENSED USERS DATABASE</b>\n━━━━━━━━━━\n" + "\n\n".join(lines) + "\n━━━━━━━━━━"
    await send_long_message(update.message, text)


async def new_user_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /new_user_list to view all free users registered on /start but not yet VIP."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied. Admin privileges required.</i>", parse_mode=ParseMode.HTML)
        return

    free_users = UserRegistry.get_free_users()
    if not free_users:
        await update.message.reply_text("📋 <b>FREE USERS LEAD DATABASE</b>\n\n<i>មិនទាន់មាន Free User ណាមួយចុះឈ្មោះឡើយ។</i>", parse_mode=ParseMode.HTML)
        return

    lines = [
        "📋 <b>FREE USERS LEAD DATABASE (មិនទាន់ក្លាយជា VIP)</b>\n"
        "━━━━━━━━━━\n"
        f"📊 <b>ចំនួន Free Leads សរុប ៖</b> <b>{len(free_users)} នាក់</b>\n"
    ]

    for idx, u in enumerate(free_users[:100], 1):
        uname = u.get("name", "User")
        u_handle = f" (@{u['username']})" if u.get("username") else ""
        u_id = u.get("id")
        u_joined = u.get("joined_at", "N/A")
        lines.append(f"{idx}. 👤 <b>{uname}</b>{u_handle}\n   🆔 ID: <code>{u_id}</code> | 📅 Joined: <code>{u_joined}</code>")

    lines.append("━━━━━━━━━━")
    lines.append("💡 <i>Admin អាចប្រើ <code>/addvip [id] [days] [name]</code> ឬ <code>/addsupervip [id] [days] [name]</code> ដើម្បីដំឡើងសិទ្ធិ!</i>")

    full_text = "\n".join(lines)
    await send_long_message(update.message, full_text)



async def novel_kh_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /novel_kh command. Restricted exclusively to Super VIP members."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Super VIP Gatekeeping Check
    if not VIPManager.is_super_vip(user.id):
        text = (
            "🌟 <b>ការកម្រិតសិទ្ធិ ៖ ទាមទារអាជ្ញាប័ណ្ណ SUPER VIP MEMBERSHIP</b>\n"
            "━━━━━━━━━━\n"
            "មុខងារពិសេស (APEX Khmer Novelist Grandmaster Engine) ត្រូវបានផ្តល់ជូនដាច់ដោយលែកសម្រាប់តែសមាជិក <b>SUPER VIP Members</b> តែប៉ុណ្ណោះ!\n\n"
            f"👤 <b>ឈ្មោះ ៖</b> {user.first_name}\n"
            f"🆔 <b>លេខ Telegram ID របស់លោកអ្នក ៖</b> <code>{user.id}</code>\n"
            "👑 <b>កម្រិតអាជ្ញាប័ណ្ណបច្ចុប្បន្ន ៖</b> VIP User (សមាជិក VIP ធម្មតា)\n\n"
            "📩 <b>ទំនាក់ទំនងដើម្បីដំឡើងទៅកាន់ SUPER VIP Membership ៖</b>\n"
            "សូមទាក់ទងទៅកាន់ Super Admin តាមរយៈ Telegram ដើម្បីបើកសិទ្ធិប្រើប្រាស់ ៖\n"
            "• <b>Telegram Admin ៖</b> <b>@Sokpheatonsai</b>\n"
            "━━━━━━━━━━"
        )
        if update.callback_query:
            await update.callback_query.message.reply_text(text, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return


    # Super VIP User Executing /novel_kh
    if not context.args:
        text = (
            "📖 <b>APEX KHMER NOVELIST GRANDMASTER ENGINE</b>\n"
            "━━━━━━━━━━\n"
            "✨ Welcome Super VIP Master! To write a deeply emotional Khmer novel chapter, type:\n\n"
            "<code>/novel_kh [បរិបទ/កាលអាកាស] [តួអង្គ] [គោលដៅ/ទំនាស់] [ជំពូក]</code>\n\n"
            "<i>ឧទាហរណ៍ ៖</i>\n"
            "<code>/novel_kh ក្រុងលង្វែក សម័យបុរាណ, តួអង្គ៖ ជ័យ និង បុប្ផា, គោលដៅ៖ ស្នេហានិងការការពារទឹកដី, ជំពូកទី ១</code>\n"
            "━━━━━━━━━━"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    prompt_details = " ".join(context.args)

    # 1. Check Persistent Novel Disk Cache (0.001s Instant Response + $0 API Cost)
    cached_novel = NovelCache.get(prompt_details)
    if cached_novel:
        await send_long_message(update.message, cached_novel)
        return

    status_msg = await update.message.reply_text("✍️ <b>កំពុងនិពន្ធប្រលោមលោកខ្មែរតាមទម្រង់ APEX Khmer Novelist Grandmaster...</b>", parse_mode=ParseMode.HTML)
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        novel_prompt = (
            f"Write an exceptionally substantial, deeply detailed, extremely long, immersive novel chapter in Khmer based on these prompt details:\n"
            f"{prompt_details}\n\n"
            f"REQUIREMENTS FOR EXTENSIVE LENGTH & DEEP DETAIL:\n"
            f"1. Do NOT summarize or rush the plot. Write extensive prose detailing setting (Kal Akas), internal thoughts, dialogue, sensory feelings, and character actions.\n"
            f"2. Follow all 4 sections of the APEX Khmer Novelist Grandmaster mandate strictly.\n"
            f"3. Output a complete, massive, long chapter (at least 1500 - 3000 words in Khmer).\n"
            f"4. Maintain zero markdown symbols (no asterisks, no rules, no bolding tags)."
        )
        raw_novel = await architect_agent.generate_novel_chapter(novel_prompt)

        sanitized = reviewer_agent.validate_and_sanitize(raw_novel, strict=Config.ZERO_MARKDOWN_STRICT)

        if sanitized and len(sanitized.strip()) > 20:
            # Save to persistent disk cache for all future users
            NovelCache.set(prompt_details, sanitized)

        # Notify Admin
        try:
            await SystemMonitor.notify_admin_live_activity(
                bot=context.bot,
                user=user,
                query=f"/novel_kh {prompt_details}",
                response=sanitized
            )
        except Exception:
            pass

        await send_long_message(update.message, sanitized)

    except Exception as err:
        logger.error(f"Khmer Novelist generation failed: {err}")
        await update.message.reply_text(f"⚠️ កើតមានបញ្ហាក្នុងការនិពន្ធប្រលោមលោក៖ {err}", parse_mode=ParseMode.HTML)


async def novel_18_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /novel_18 command. Strictly restricted to ADMIN ONLY; completely hidden from normal users."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # 1. Strict Admin Gatekeeper: Mask command completely from non-admin users
    if not is_admin(user.id):
        # Absolutely zero disclosure: act as if the command does not exist
        if update.callback_query:
            await update.callback_query.message.reply_text("❌ មិនមានបញ្ជា (Command) នេះឡើយ។ សូមចុច /help ដើម្បីមើលបញ្ជីមុខងារ។", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ មិនមានបញ្ជា (Command) នេះឡើយ។ សូមចុច /help ដើម្បីមើលបញ្ជីមុខងារ។", parse_mode=ParseMode.HTML)
        return

    # 2. Super Smart Admin Console
    if not context.args:
        text = (
            "⚡ <b>SUPER SMART NOVEL 18+ ENGINE (ADMIN SECRET CONSOLE)</b>\n"
            "━━━━━━━━━━\n"
            "👑 <b>សូមស្វាគមន៍ Super Admin!</b> មុខងារនេះត្រូវបានចាក់សោសម្ងាត់សម្រាប់តែ Admin ប៉ុណ្ណោះ (Users ធម្មតាមើលមិនឃើញឡើយ)។\n\n"
            "<b>របៀបប្រើប្រាស់ (Admin Command Syntax) ៖</b>\n"
            "<code>/novel_18 [HEAT 1-5] [ជំពូកទី N] [សាច់រឿង/តួអង្គ]</code>\n\n"
            "<i>ឧទាហរណ៍ ជាក់ស្តែង ៖</i>\n"
            "<code>/novel_18 4 ជំពូកទី ១ តួប្រុសជា CEO ត្រជាក់ តួស្រីជាលេខា ជាប់ក្នុងជណ្តើរយន្តពេលភ្លើងដាច់</code>\n\n"
            "🔥 <b>កម្រិតកម្តៅ (HEAT LEVELS) ៖</b>\n"
            "• <b>Level 1 (Sweet):</b> មនោសញ្ចេតនាផ្អែមល្ហែម កាន់ដៃ ឱប ថើបថ្ងាស\n"
            "• <b>Level 2 (Warm):</b> ថើបបឺតមាត់យ៉ាងស្រទន់ និងក្តីស្រលាញ់ជ្រាលជ្រៅ\n"
            "• <b>Level 3 (Sensual):</b> ឈុតស្នេហា Sensual បង្ហាញអារម្មណ៍កក់ក្តៅ និងភាពស្និទ្ធស្នាល\n"
            "• <b>Level 4 (Spicy/Hot):</b> ពិពណ៌នាយ៉ាងលម្អិតអំពីកាយវិការ និងអារម្មណ៍រំភើបញាប់ញ័រ\n"
            "• <b>Level 5 (Extra Spicy):</b> ពិពណ៌នាគ្រប់ឈុតឆាកមនោសញ្ចេតនាយ៉ាងស៊ីជម្រៅបំផុត\n\n"
            "🧠 <b>សមត្ថភាព Super Smart ៖</b>\n"
            "• <b>Auto Chapter Continuity:</b> ចងចាំសាច់រឿងឆ្លងជំពូកស្វ័យប្រវត្តិ\n"
            "• <b>Instant Disk Cache (0.001s):</b> មិនខាត Quota API ពេលហៅជំពូកដដែល\n"
            "• <b>Literary Grandmaster:</b> អក្សរសាស្ត្រខ្មែរផ្ចិតផ្ចង់កម្រិតខ្ពស់ គ្មាននិមិត្តសញ្ញារញ៉េរញ៉ៃ\n"
            "━━━━━━━━━━"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    prompt_details = " ".join(context.args)

    # 1. Check Persistent Novel Disk Cache (0.001s Instant Response + $0 API Cost)
    cached_novel = Novel18Cache.get(prompt_details)
    if cached_novel:
        await send_long_message(update.message, cached_novel)
        return

    status_msg = await update.message.reply_text("✍️ <b>កំពុងនិពន្ធប្រលោមលោកតាមទម្រង់ Super Smart Admin Engine...</b>", parse_mode=ParseMode.HTML)
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # Extract target chapter and heat level if specified
        target_chapter = 1
        heat_level = 5
        match_chap = re.search(r"ជំពូកទី\s*(\d+)|chapter\s*(\d+)", prompt_details, re.IGNORECASE)
        if match_chap:
            target_chapter = int(match_chap.group(1) or match_chap.group(2) or 1)

        match_heat = re.search(r"\b([1-5])\b", prompt_details)
        if match_heat:
            heat_level = int(match_heat.group(1))

        continuity_context = NovelContinuityTracker.get_novel_context(user.id, target_chapter)
        lexicon_context = KhmerRomanceLexicon.get_lexicon_prompt_injection(heat_level)

        novel_prompt = (
            f"Write an exceptionally substantial, deeply detailed, extremely long, immersive romance novel chapter in Khmer based on these prompt details:\n"
            f"{prompt_details}\n\n"
            f"HEAT LEVEL: Level {heat_level} (Strictly maintained across the entire chapter)\n"
            f"TARGET CHAPTER: Chapter {target_chapter}\n"
            f"{lexicon_context}\n"
            f"{continuity_context}\n\n"
            f"REQUIREMENTS FOR EXTENSIVE LENGTH & SEAMLESS CONTINUITY:\n"
            f"1. Do NOT summarize or rush the plot. Write extensive prose detailing setting, internal thoughts, dialogue, sensory feelings, and character actions.\n"
            f"2. Apply all 4 layers of the framework (Skin, Blood, Muscle, Mind) in full depth with maximum emotional & physical description.\n"
            f"3. Ensure 100% story continuity with previous chapters. Never confuse character names, roles, or skip character developments.\n"
            f"4. Output a complete, massive, long chapter (at least 1500 - 3000 words in Khmer).\n"
            f"5. Maintain zero markdown symbols (no asterisks, no rules, no bolding tags)."
        )
        raw_novel = await architect_agent.generate_novel_18_chapter(novel_prompt)

        sanitized = reviewer_agent.validate_and_sanitize(raw_novel, strict=Config.ZERO_MARKDOWN_STRICT)

        if sanitized and len(sanitized.strip()) > 20:
            # Save to persistent disk cache & continuity tracker
            Novel18Cache.set(prompt_details, sanitized)
            NovelContinuityTracker.update_novel_state(user.id, heat_level, prompt_details, target_chapter, sanitized)

        # Notify Admin (if executed from outside primary admin chat)
        try:
            await SystemMonitor.notify_admin_live_activity(
                bot=context.bot,
                user=user,
                query=f"/novel_18 {prompt_details}",
                response=sanitized
            )
        except Exception:
            pass

        await send_long_message(update.message, sanitized)

    except Exception as err:
        logger.error(f"Super Smart Novel generation failed: {err}")
        await update.message.reply_text(f"⚠️ កើតមានបញ្ហាក្នុងការនិពន្ធប្រលោមលោក ៖ {err}", parse_mode=ParseMode.HTML)


async def master_prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /master_prompt command. Restricted exclusively to Super VIP members."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Super VIP Gatekeeping Check
    if not VIPManager.is_super_vip(user.id):
        text = (
            "🌟 <b>ការកម្រិតសិទ្ធិ ៖ ទាមទារអាជ្ញាប័ណ្ណ SUPER VIP MEMBERSHIP</b>\n"
            "━━━━━━━━━━\n"
            "មុខងារពិសេស (APEX AGI Prompt Genesis Node /master_prompt) ត្រូវបានផ្តល់ជូនដាច់ដោយលែកសម្រាប់តែសមាជិក <b>SUPER VIP Members</b> តែប៉ុណ្ណោះ!\n\n"
            f"👤 <b>ឈ្មោះ ៖</b> {user.first_name}\n"
            f"🆔 <b>លេខ Telegram ID របស់លោកអ្នក ៖</b> <code>{user.id}</code>\n"
            "👑 <b>កម្រិតអាជ្ញាប័ណ្ណបច្ចុប្បន្ន ៖</b> VIP User (សមាជិក VIP ធម្មតា)\n\n"
            "📩 <b>ទំនាក់ទំនងដើម្បីដំឡើងទៅកាន់ SUPER VIP Membership ៖</b>\n"
            "សូមទាក់ទងទៅកាន់ Super Admin តាមរយៈ Telegram ដើម្បីបើកសិទ្ធិប្រើប្រាស់ ៖\n"
            "• <b>Telegram Admin ៖</b> <b>@Sokpheatonsai</b>\n"
            "━━━━━━━━━━"
        )
        if update.callback_query:
            await update.callback_query.message.reply_text(text, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    # Super VIP User Executing /master_prompt
    if not context.args:
        text = (
            "💡 <b>APEX AGI PROMPT GENESIS ENGINE (MASTER PROMPT)</b>\n"
            "━━━━━━━━━━\n"
            "✨ ស្វាគមន៍ Super VIP Master! នេះជា «រោងចក្រផលិតកំពូល Prompts» (The Genesis Node) ដែលអាចបង្កើតកូដបញ្ជា English Master Prompt កម្រិត AGI សម្រាប់យកទៅប្រើប្រាស់បន្ត ៖\n\n"
            "<code>/master_prompt [ប្រធានបទ/គោលដៅ/ជំនាញដែលចង់បាន]</code>\n\n"
            "<i>ឧទាហរណ៍ ៖</i>\n"
            "• <code>/master_prompt អ្នកជំនាញវិភាគទិន្នន័យហិរញ្ញវត្ថុ និង Crypto Trading Analyst</code>\n"
            "• <code>/master_prompt គ្រូបង្រៀនកូដ Python និង Full Stack Web Developer</code>\n"
            "• <code>/master_prompt អ្នកនិពន្ធសៀវភៅជំនួញ និង Marketing Strategy Expert</code>\n"
            "━━━━━━━━━━"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        return

    concept_details = " ".join(context.args)

    # 1. Check Persistent Master Prompt Disk Cache (0.001s Instant Response + $0 API Cost)
    cached_master_prompt = MasterPromptCache.get(concept_details)
    if cached_master_prompt:
        await send_long_message(update.message, cached_master_prompt)
        return

    status_msg = await update.message.reply_text("⚙️ <b>កំពុងសរសេរ English Master Prompt កម្រិត AGI Prompt Genesis Node...</b>", parse_mode=ParseMode.HTML)
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        raw_master_prompt = await architect_agent.generate_master_prompt(concept_details)
        sanitized = reviewer_agent.validate_and_sanitize(raw_master_prompt, strict=Config.ZERO_MARKDOWN_STRICT)

        if sanitized and len(sanitized.strip()) > 20:
            # Save to persistent disk cache for all future users
            MasterPromptCache.set(concept_details, sanitized)

        # Notify Admin
        try:
            await SystemMonitor.notify_admin_live_activity(
                bot=context.bot,
                user=user,
                query=f"/master_prompt {concept_details}",
                response=sanitized
            )
        except Exception:
            pass

        await send_long_message(update.message, sanitized)

    except Exception as err:
        logger.error(f"Master Prompt generation failed: {err}")
        await update.message.reply_text(f"⚠️ កើតមានបញ្ហាក្នុងការបង្កើត Master Prompt ៖ {err}", parse_mode=ParseMode.HTML)





async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Handles interactive button taps for course selection, admin controls, and lesson execution."""
    query = update.callback_query
    try:
        await query.answer()
    except Exception as ans_err:
        logger.debug(f"Callback answer notice: {ans_err}")
    data = query.data

    parts = data.split(":")
    action = parts[0]

    if action != "admin":
        if not await check_vip_access(update, context):
            return


    if action == "admin":
        sub = parts[1]
        if sub == "status":
            await status_command(update, context)
        elif sub == "models":
            await models_command(update, context)
        elif sub == "toggle_vip":
            await vip_toggle_command(update, context)
        elif sub == "clearcache":
            await clearcache_command(update, context)
        elif sub == "refresh":
            await admin_panel_command(update, context)
        return

    if action == "course":
        course_key = parts[1]
        page = int(parts[2]) if len(parts) > 2 else 1
        course_info = AI_COURSES.get(course_key, AI_COURSES["gemini"])

        text = (
            f"<b>{course_info['emoji']} {course_info['title']}</b>\n"
            f"<i>{course_info['desc']}</i>\n\n"
            f"<b>📚 បញ្ជីមេរៀន (ទំព័រទី {page} / 10 - មេរៀនទី {(page-1)*10+1} ដល់ {page*10}) ៖</b>\n"
            f"ចុចលើមេរៀនណាមួយខាងក្រោមដើម្បីចាប់ផ្តើមរៀនសូត្រលម្អិត ១០០% ៖"
        )

        keyboard = []
        start_lesson = (page - 1) * 10 + 1
        end_lesson = page * 10

        for l_num in range(start_lesson, end_lesson + 1):
            l_title = CurriculumEngine.get_lesson_title(course_key, l_num, lang="km")
            keyboard.append([InlineKeyboardButton(f"📖 {l_title}", callback_data=f"lesson:{course_key}:{l_num}")])

        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton("◀ ថយក្រោយ", callback_data=f"course:{course_key}:{page-1}"))
        nav_row.append(InlineKeyboardButton("🏠 មុខជំនាញទាំងអស់", callback_data="courses_list"))
        if page < 10:
            nav_row.append(InlineKeyboardButton("បន្ទាប់ ▶", callback_data=f"course:{course_key}:{page+1}"))
        keyboard.append(nav_row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif action == "study_mode":
        target_mode = parts[1]
        user = update.effective_user
        applied_mode = StudentManager.set_learning_mode(user.id, target_mode)
        user_state = state_manager.get_state(query.message.chat_id)
        user_state.set_learning_mode(applied_mode)

        mode_label = "⚡ របៀបសូក្រាតអន្តរកម្ម (Interactive Socratic)" if applied_mode == "socratic" else "📘 របៀបពន្យល់ក្បោះក្បាយ (Explanatory)"
        try:
            await query.answer(f"បានកំណត់៖ {mode_label}", show_alert=False)
        except Exception:
            pass
        await study_command(update, context)

    elif action == "study_profile":
        await study_command(update, context)

    elif action == "courses_list":
        await ai_courses_command(update, context)

    elif action == "lesson":
        course_key = parts[1]
        lesson_num = int(parts[2])
        chat_id = query.message.chat_id
        user = update.effective_user

        learning_mode = StudentManager.get_learning_mode(user.id)
        lesson_title = CurriculumEngine.get_lesson_title(course_key, lesson_num, lang="km")

        # 1. Check Persistent Disk Lesson Cache (0.001s Instant Response + $0 API Cost)
        cache_lang_key = f"km_{learning_mode}"
        cached_sanitized = LessonCache.get(course_key, lesson_num, lang=cache_lang_key)

        # Invalidate broken/corrupted cache entries from previous runs
        if cached_sanitized:
            if "&#x27;" in cached_sanitized or "&quot;" in cached_sanitized or "<pre><code" not in cached_sanitized:
                logger.warning(f"Invalidating corrupted cached lesson for {course_key}:{lesson_num}")
                cached_sanitized = None
            else:
                cached_sanitized = ReviewerAgent.balance_html_tags(cached_sanitized)

        # Clean 1-click UX: Instant acknowledgement without lingering chat messages
        try:
            await query.answer()
        except Exception:
            pass

        # Native non-intrusive typing activity in chat header (no chat message bubbles)
        if not cached_sanitized:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        try:
            if cached_sanitized:
                sanitized = cached_sanitized
            else:
                prompt = CurriculumEngine.generate_lesson_prompt(course_key, lesson_num, lang="km", mode=learning_mode)
                user_state = state_manager.get_state(chat_id)
                intent = evaluator_agent.analyze(prompt)

                raw_response = await architect_agent.generate_response(user_query=prompt, user_state=user_state, intent=intent)
                sanitized = reviewer_agent.validate_and_sanitize(text=raw_response, strict=Config.ZERO_MARKDOWN_STRICT)

                if not sanitized or len(sanitized.strip()) < 10:
                    sanitized = f"📘 <b>{lesson_title}</b>\n\nប្រព័ន្ធកំពុងរៀបចំខ្លឹមសារមេរៀននេះឡើងវិញ។ សូមចុចប៊ូតុងខាងក្រោមដើម្បីព្យាយាមម្តងទៀត ឬបន្តទៅមេរៀនបន្ទាប់។"
                else:
                    # Save to persistent disk cache for all future users
                    LessonCache.set(course_key, lesson_num, cache_lang_key, sanitized)

            user_state = state_manager.get_state(chat_id)
            user_state.add_turn(role="user", content=f"Lesson Request ({learning_mode}): {lesson_title}")
            user_state.add_turn(role="model", content=sanitized)

            # Update Student Course Progress & Active Socratic Challenge
            StudentManager.update_course_progress(user.id, course_key, lesson_num)
            if learning_mode == "socratic":
                StudentManager.set_active_exercise(user.id, {
                    "course_key": course_key,
                    "lesson_num": lesson_num,
                    "lesson_title": lesson_title,
                    "prompt": sanitized[:400]
                })

            # Safe async notification to admin
            try:
                await SystemMonitor.notify_admin_live_activity(
                    bot=context.bot,
                    user=update.effective_user,
                    query=f"Requested Lesson ({learning_mode}): {lesson_title}",
                    response=sanitized
                )
            except Exception as admin_err:
                logger.warning(f"Admin alert notice: {admin_err}")

            keyboard = [
                [
                    InlineKeyboardButton("📖 មេរៀនបន្ទាប់ ▶", callback_data=f"lesson:{course_key}:{min(100, lesson_num+1)}"),
                    InlineKeyboardButton("📚 បញ្ជីមេរៀន", callback_data=f"course:{course_key}:{(lesson_num-1)//10+1}")
                ],
                [
                    InlineKeyboardButton("🎓 មើលកាតពិន្ទុ (/study)", callback_data="study_profile")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await send_long_message(query.message, sanitized, reply_markup=reply_markup)

        except Exception as err:
            logger.error(f"Failed to generate lesson {lesson_title}: {err}", exc_info=True)
            escaped_err = py_html.escape(str(err))
            await query.message.reply_text(
                f"⚠️ <b>មានបញ្ហាក្នុងការទាញយកមេរៀន៖</b> {escaped_err}\n\nសូមព្យាយាមចុចរៀនម្តងទៀត ឬជ្រើសរើសមេរៀនផ្សេង។",
                parse_mode=ParseMode.HTML
            )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /help command detailing cognitive features in 100% Khmer."""
    help_text = (
        "✨ <b>ស្ថាបត្យកម្ម POLYMATH AI GRANDMASTER</b>\n"
        "━━━━━━━━━━\n"
        "១. <b>១០០ មេរៀនក្នុង ១ ជំនាញ (100-Lesson Master Curriculum) ៖</b> ចូលរៀនមេរៀន AI Masterclasses ទាំង ៧០០ មេរៀន ដោយប្រើប្រាស់បញ្ជា <b>/ai</b>។\n"
        "២. <b>បំបែកគំនិតស្មុគស្មាញ (First-Principles Deconstruction) ៖</b> បំប្លែងទ្រឹស្តី និងកូដស្មុគស្មាញ ទៅជាការយល់ដឹងបែបធម្មជាតិ និងច្បាស់លាស់។\n"
        "៣. <b>បណ្តាញខួរក្បាល Multi-Agent ៖</b> ប្រព័ន្ធស្កែនបំណង (Evaluator) -> ប្រព័ន្ធបង្កើតចម្លើយ (Architect) -> ប្រព័ន្ធកែសម្រួលអក្សរសាស្ត្រ (Reviewer)។\n"
        "៤. <b>ប្រព័ន្ធចងចាំបរិបទសន្ទនា (Sliding-Window Memory) ៖</b> ចងចាំប្រវត្តិសន្ទនាស្វ័យប្រវត្តិ។\n\n"
        "💡 ប្រើប្រាស់ <b>/ai</b> ដើម្បីមើលបញ្ជីមេរៀន ឬ <b>/reset</b> ដើម្បីលុបប្រវត្តិសន្ទនាចាស់។\n"
        "━━━━━━━━━━"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)



async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /reset command to clear user context memory."""
    chat_id = update.effective_chat.id
    state_manager.reset_state(chat_id)
    await update.message.reply_text("Conversation state and memory thread have been reset.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Orchestrates incoming message processing through the Multi-Agent Cognitive Pipeline."""
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    if user:
        is_spam, cooldown = AntiSpamGuard.is_spamming(user.id)
        if is_spam:
            await update.message.reply_text(
                f"⚠️ <b>ប្រព័ន្ធសុវត្ថិភាព ANTI-SPAM GUARD ACTIVE ៖</b>\n"
                f"លោកអ្នកបានផ្ញើសារញឹកញាប់ពេក (Flood Protection)។ សូមរង់ចាំ <b>{cooldown} វិនាទី</b> ទៀត មុននឹងផ្ញើសារបន្ទាប់។",
                parse_mode=ParseMode.HTML
            )
            return

    user_query = update.message.text.strip()
    user_query = PromptInjectionGuard.sanitize_query(user_query)

    # Route /novel_18 or /novel_18+ text commands gracefully (STRICT ADMIN ONLY)
    if (user_query.startswith("/novel_18") or user_query.startswith("/Novel_18") or 
        user_query.startswith("/novel18") or user_query.startswith("/Novel18")):
        if not is_admin(user.id):
            await update.message.reply_text("❌ មិនមានបញ្ជា (Command) នេះឡើយ។ សូមចុច /help ដើម្បីមើលបញ្ជីមុខងារ។", parse_mode=ParseMode.HTML)
            return
        context.args = user_query.split()[1:]
        await novel_18_command(update, context)
        return

    # Route /master_prompt text commands gracefully
    if user_query.startswith("/master_prompt") or user_query.startswith("/Master_Prompt") or user_query.startswith("/masterprompt"):
        context.args = user_query.split()[1:]
        await master_prompt_command(update, context)
        return


    if not await check_vip_access(update, context):
        return

    chat_id = update.effective_chat.id

    # Check if student is responding to an active Socratic challenge
    active_ex = StudentManager.get_active_exercise(user.id)
    if active_ex and not user_query.startswith("/"):
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        eval_result = await ReviewerAgent.evaluate_student_understanding(
            student_answer=user_query,
            exercise_title=active_ex.get("lesson_title", "Socratic Challenge"),
            lesson_context=active_ex.get("prompt", ""),
            architect_agent=architect_agent
        )

        points_earned = eval_result.get("points", 15)
        passed = eval_result.get("passed", True)
        feedback_content = eval_result.get("feedback", "")

        # Atomically record exercise result in StudentManager
        res = StudentManager.record_exercise_result(
            user_id=user.id,
            points=points_earned,
            exercise_title=active_ex.get("lesson_title", "Socratic Challenge"),
            feedback=feedback_content,
            passed=passed
        )

        c_key = active_ex.get("course_key", "gemini")
        l_num = active_ex.get("lesson_num", 1)
        next_l_num = min(100, l_num + 1)

        eval_header = (
            f"🏆 <b>ពិន្ទុថ្មី ៖</b> <b>+{points_earned} ពិន្ទុ</b> (ពិន្ទុសរុប៖ <b>{res['new_score']} ពិន្ទុ</b>)\n"
            f"🎖️ <b>កម្រិតសមត្ថភាព ៖</b> {res['level_emoji']} <b>{res['level_title']}</b>\n"
            f"📝 <b>លំហាត់បានបញ្ចប់សរុប ៖</b> <b>{res['completed_count']} លំហាត់</b>\n"
            "━━━━━━━━━━\n\n"
        )
        full_eval_response = eval_header + feedback_content

        keyboard = [
            [
                InlineKeyboardButton("📖 មេរៀនបន្ទាប់ ▶", callback_data=f"lesson:{c_key}:{next_l_num}"),
                InlineKeyboardButton("🎓 មើលកាតពិន្ទុ (/study)", callback_data="study_profile")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user_state = state_manager.get_state(chat_id)
        user_state.add_turn(role="user", content=f"Student Solution: {user_query}")
        user_state.add_turn(role="model", content=full_eval_response)

        try:
            await SystemMonitor.notify_admin_live_activity(
                bot=context.bot,
                user=user,
                query=f"Socratic Submission for {active_ex.get('lesson_title')}: {user_query[:60]}",
                response=full_eval_response
            )
        except Exception:
            pass

        await send_long_message(update.message, full_eval_response, reply_markup=reply_markup)
        return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    user_state = state_manager.get_state(chat_id)
    intent = evaluator_agent.analyze(user_query)
    raw_response = await architect_agent.generate_response(user_query=user_query, user_state=user_state, intent=intent)
    sanitized_response = reviewer_agent.validate_and_sanitize(text=raw_response, strict=Config.ZERO_MARKDOWN_STRICT)

    user_state.add_turn(role="user", content=user_query)
    user_state.add_turn(role="model", content=sanitized_response)

    # Notify admin of live VIP user activity
    await SystemMonitor.notify_admin_live_activity(
        bot=context.bot,
        user=update.effective_user,
        query=user_query,
        response=sanitized_response
    )

    await send_long_message(update.message, sanitized_response)



def setup_handlers(application: Application) -> None:
    """Registers all command, callback, and message handlers."""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ai", ai_courses_command))
    application.add_handler(CommandHandler("courses", ai_courses_command))
    application.add_handler(CommandHandler("study", study_command))
    application.add_handler(CommandHandler("socratic", study_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_panel_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("models", models_command))
    application.add_handler(CommandHandler("vip", vip_toggle_command))
    application.add_handler(CommandHandler("clearcache", clearcache_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("backup", backup_command))

    
    # VIP & Super VIP License Management Commands
    application.add_handler(CommandHandler("addvip", addvip_command))
    application.add_handler(CommandHandler("addsupervip", addsupervip_command))
    application.add_handler(CommandHandler("delvip", delvip_command))
    application.add_handler(CommandHandler("delsupervip", delvip_command))
    application.add_handler(CommandHandler("viplist", viplist_command))
    application.add_handler(CommandHandler("superviplist", viplist_command))
    application.add_handler(CommandHandler("new_user_list", new_user_list_command))
    application.add_handler(CommandHandler("newuserlist", new_user_list_command))

    # Super VIP Creative Commands
    application.add_handler(CommandHandler("novel_kh", novel_kh_command))
    application.add_handler(CommandHandler("Novel_kh", novel_kh_command))
    application.add_handler(CommandHandler("master_prompt", master_prompt_command))
    application.add_handler(CommandHandler("Master_prompt", master_prompt_command))
    application.add_handler(CommandHandler("Master_Prompt", master_prompt_command))
    application.add_handler(CommandHandler("masterprompt", master_prompt_command))

    # Secret Admin Only Commands (Completely hidden from users)
    application.add_handler(CommandHandler("novel_18", novel_18_command))
    application.add_handler(CommandHandler("Novel_18", novel_18_command))
    application.add_handler(CommandHandler("novel18", novel_18_command))
    application.add_handler(CommandHandler("Novel18", novel_18_command))

    application.add_handler(CallbackQueryHandler(handle_callback_query))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(global_error_handler)


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catches unhandled errors and logs them gracefully without system disruption."""
    err = context.error
    if "Query is too old" in str(err) or "query id is invalid" in str(err):
        logger.debug(f"Expired callback query safely ignored: {err}")
    elif "httpx.ReadError" in str(err) or "NetworkError" in str(err):
        logger.warning(f"Telegram network transient event: {err}")
    else:
        logger.error(f"Telegram update caused error: {err}", exc_info=context.error)





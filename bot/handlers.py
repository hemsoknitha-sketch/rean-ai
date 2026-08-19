"""Telegram Bot Command and Message Handlers with Interactive AI Course, 100-Lesson Curriculum Engine, & Super Admin Suite."""
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

logger = logging.getLogger(__name__)

# Initialize cognitive components
state_manager = StateManager(max_turns=Config.MAX_MEMORY_TURNS)
evaluator_agent = EvaluatorAgent()
architect_agent = ArchitectAgent()
reviewer_agent = ReviewerAgent()


def is_admin(user_id: int) -> bool:
    """Checks if the user ID matches Config.ADMIN_CHAT_ID or 859271875."""
    return user_id == Config.ADMIN_CHAT_ID or user_id == 859271875


async def send_long_message(target_msg, text: str, reply_markup=None) -> None:
    """Splits long text (>3900 chars) into clean paragraph chunks so no text is ever truncated."""
    max_len = 3900
    if len(text) <= max_len:
        try:
            await target_msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        except Exception:
            plain_text = re.sub(r"<[^>]+>", "", text)
            await target_msg.reply_text(plain_text, reply_markup=reply_markup)
        return

    # Split into paragraph chunks safely
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for p in paragraphs:
        if current_length + len(p) + 2 > max_len:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_length = len(p)
        else:
            current_chunk.append(p)
            current_length += len(p) + 2

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    for i, chunk in enumerate(chunks):
        is_last = (i == len(chunks) - 1)
        m_markup = reply_markup if is_last else None
        try:
            await target_msg.reply_text(chunk, parse_mode=ParseMode.HTML, reply_markup=m_markup)
        except Exception:
            plain_text = re.sub(r"<[^>]+>", "", chunk)
            await target_msg.reply_text(plain_text, reply_markup=m_markup)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Handles /start command with a trilingual Polymath Grandmaster greeting."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    state_manager.reset_state(chat_id)
    SystemMonitor.active_users.add(chat_id)

    greeting = (
        f"Greetings <b>{user.first_name}</b>.\n\n"
        "I am the Supreme Polymath AI Grandmaster, an elite cognitive intelligence designed to deliver "
        "master-level AI courses (100 lessons per AI topic) across computer science, mathematics, and philosophy.\n\n"
        "• ភាសាខ្មែរ: ខ្ញុំត្រៀមខ្លួនជាស្រេចក្នុងការបង្រៀន ១០០ មេរៀន ក្នុង ១ ជំនាញ AI លម្អិតឥតលាក់បាំង។\n"
        "• English: Ask any query or select an AI Course from the menu below to begin learning.\n\n"
        f"🆔 <b>Your Telegram User ID:</b> <code>{user.id}</code>\n\n"
        "<b>Commands:</b>\n"
        "/ai - 🎓 បើកបញ្ជី AI Courses ទាំងអស់ (100 Lessons per AI)\n"
        "/start - Re-initialize dialogue\n"
        "/reset - Clear conversation memory\n"
        "/help - View Grandmaster capabilities"
    )

    if is_admin(user.id):
        greeting += "\n\n👑 <b>Super Admin Panel Access Authorized:</b> Use /admin to open VIP Dashboard."

    keyboard = []
    for key, info in AI_COURSES.items():
        keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['title']}", callback_data=f"course:{key}:1")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(greeting, parse_mode=ParseMode.HTML, reply_markup=reply_markup)



async def ai_courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /ai or /courses command to display interactive AI learning menu."""
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


async def admin_panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /admin command for Super Admin Control Panel."""
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ <i>Access Denied: Only Super Admin ID 859271875 can execute this command.</i>", parse_mode=ParseMode.HTML)
        return

    text = (
        "👑 <b>SUPER ADMIN CONTROL PANEL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Admin ID:</b> <code>{user.id}</code>\n"
        f"<b>VIP Alerts:</b> {'🟢 ENABLED' if SystemMonitor.vip_alerts_enabled else '🔴 DISABLED'}\n"
        f"<b>Active Engine:</b> {'🤖 Local Model' if Config.USE_LOCAL_MODEL else '⚡ Gemini 3.6 Flash'}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
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
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ <b>Service Status:</b> 🟢 ACTIVE (running)\n"
        f"⏱️ <b>Bot Uptime:</b> {health['uptime']}\n"
        f"💻 <b>CPU Usage:</b> {health['cpu_percent']}%\n"
        f"🧠 <b>RAM Memory:</b> {health['ram_used_gb']} GB / {health['ram_total_gb']} GB ({health['ram_percent']}%)\n"
        f"💾 <b>Disk Storage:</b> {health['disk_used_gb']} GB / {health['disk_total_gb']} GB (Free: {health['disk_free_gb']} GB - {health['disk_percent']}%)\n"
        f"👥 <b>Active Users Count:</b> {health['active_users_count']}\n"
        "━━━━━━━━━━━━━━━━━━━━━"
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
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>Active Provider:</b> {status['engine_type']}\n"
        f"🎯 <b>Current Model:</b> <code>{status['active_model']}</code>\n"
        f"🌐 <b>Ollama Server (11434):</b> {'🟢 ONLINE' if status['ollama_online'] else '🔴 OFFLINE'}\n\n"
        f"<b>Installed Ollama Models:</b>\n{models_str}\n"
        "━━━━━━━━━━━━━━━━━━━━━"
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
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "To send a broadcast announcement to all active users, please type:\n\n"
            "<code>/broadcast Your Announcement Text Here</code>\n\n"
            "<i>Example:</i> <code>/broadcast 🚀 New AI Course Lessons are now available! Click /ai to learn.</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━"
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



async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles interactive button taps for course selection, admin controls, and lesson execution."""
    query = update.callback_query
    await query.answer()
    data = query.data

    parts = data.split(":")
    action = parts[0]

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

    elif action == "courses_list":
        await ai_courses_command(update, context)

    elif action == "lesson":
        course_key = parts[1]
        lesson_num = int(parts[2])
        chat_id = query.message.chat_id

        lesson_title = CurriculumEngine.get_lesson_title(course_key, lesson_num, lang="km")
        status_msg = await query.message.reply_text(f"⏳ <b>កំពុងរៀបចំមេរៀន៖ {lesson_title}...</b>", parse_mode=ParseMode.HTML)
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        try:
            prompt = CurriculumEngine.generate_lesson_prompt(course_key, lesson_num, lang="km")
            user_state = state_manager.get_state(chat_id)
            intent = evaluator_agent.analyze(prompt)

            raw_response = await architect_agent.generate_response(user_query=prompt, user_state=user_state, intent=intent)
            sanitized = reviewer_agent.validate_and_sanitize(text=raw_response, strict=Config.ZERO_MARKDOWN_STRICT)

            if not sanitized or len(sanitized.strip()) < 10:
                sanitized = f"📘 <b>{lesson_title}</b>\n\nប្រព័ន្ធកំពុងរៀបចំខ្លឹមសារមេរៀននេះឡើងវិញ។ សូមចុចប៊ូតុងខាងក្រោមដើម្បីព្យាយាមម្តងទៀត ឬបន្តទៅមេរៀនបន្ទាប់។"

            user_state.add_turn(role="user", content=f"Lesson Request: {lesson_title}")
            user_state.add_turn(role="model", content=sanitized)

            # Safe async notification to admin
            try:
                await SystemMonitor.notify_admin_live_activity(
                    bot=context.bot,
                    user=update.effective_user,
                    query=f"Requested Lesson: {lesson_title}",
                    response=sanitized
                )
            except Exception as admin_err:
                logger.warning(f"Admin alert notice: {admin_err}")

            keyboard = [
                [
                    InlineKeyboardButton("📖 មេរៀនបន្ទាប់ ▶", callback_data=f"lesson:{course_key}:{min(100, lesson_num+1)}"),
                    InlineKeyboardButton("📚 បញ្ជីមេរៀន", callback_data=f"course:{course_key}:{(lesson_num-1)//10+1}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await send_long_message(query.message, sanitized, reply_markup=reply_markup)

        except Exception as err:
            logger.error(f"Failed to generate lesson {lesson_title}: {err}", exc_info=True)
            await query.message.reply_text(
                f"⚠️ <b>មានបញ្ហាក្នុងការទាញយកមេរៀន៖</b> {err}\n\nសូមព្យាយាមចុចរៀនម្តងទៀត ឬជ្រើសរើសមេរៀនផ្សេង។",
                parse_mode=ParseMode.HTML
            )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /help command detailing cognitive features."""
    help_text = (
        "<b>Polymath AI Grandmaster Architecture:</b>\n\n"
        "1. <b>100-Lesson Master Curriculum:</b> Access 100 detailed lessons per AI subject using /ai command.\n"
        "2. <b>First-Principles Deconstruction:</b> Complex technical concepts translated into clear intuition.\n"
        "3. <b>Multi-Agent Reasoning:</b> Evaluator classification -> Architect synthesis -> Reviewer sanitization.\n"
        "4. <b>Sliding-Window Memory:</b> Remembers prior dialogue context automatically.\n\n"
        "Use /ai to browse courses or /reset to start a fresh thread."
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

    chat_id = update.effective_chat.id
    user_query = update.message.text.strip()
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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_panel_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("models", models_command))
    application.add_handler(CommandHandler("vip", vip_toggle_command))
    application.add_handler(CommandHandler("clearcache", clearcache_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))

    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

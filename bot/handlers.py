"""Telegram Bot Command and Message Handlers with Interactive AI Course & 100-Lesson Curriculum Engine."""
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

logger = logging.getLogger(__name__)

# Initialize cognitive components
state_manager = StateManager(max_turns=Config.MAX_MEMORY_TURNS)
evaluator_agent = EvaluatorAgent()
architect_agent = ArchitectAgent()
reviewer_agent = ReviewerAgent()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start command with a trilingual Polymath Grandmaster greeting."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    state_manager.reset_state(chat_id)

    greeting = (
        f"Greetings <b>{user.first_name}</b>.\n\n"
        "I am the Supreme Polymath AI Grandmaster, an elite cognitive intelligence designed to deliver "
        "master-level AI courses (100 lessons per AI topic) across computer science, mathematics, and philosophy.\n\n"
        "• ភាសាខ្មែរ: ខ្ញុំត្រៀមខ្លួនជាស្រេចក្នុងការបង្រៀន ១០០ មេរៀន ក្នុង ១ ជំនាញ AI លម្អិតឥតលាក់បាំង។\n"
        "• English: Ask any query or select an AI Course from the menu below to begin learning.\n\n"
        "<b>Commands:</b>\n"
        "/ai - 🎓 បើកបញ្ជី AI Courses ទាំងអស់ (100 Lessons per AI)\n"
        "/start - Re-initialize dialogue\n"
        "/reset - Clear conversation memory\n"
        "/help - View Grandmaster capabilities"
    )
    
    # Inline buttons for AI Courses
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


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles interactive button taps for course selection, lesson navigation, and lesson execution."""
    query = update.callback_query
    await query.answer()
    data = query.data

    parts = data.split(":")
    action = parts[0]

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

        # Pagination row
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
        await query.message.reply_text(f"⏳ <b>កំពុងរៀបចំមេរៀន៖ {lesson_title}...</b>", parse_mode=ParseMode.HTML)
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        # Generate complete masterclass prompt
        prompt = CurriculumEngine.generate_lesson_prompt(course_key, lesson_num, lang="km")
        user_state = state_manager.get_state(chat_id)
        intent = evaluator_agent.analyze(prompt)

        raw_response = await architect_agent.generate_response(user_query=prompt, user_state=user_state, intent=intent)
        sanitized = reviewer_agent.validate_and_sanitize(text=raw_response, strict=Config.ZERO_MARKDOWN_STRICT)

        user_state.add_turn(role="user", content=f"Lesson Request: {lesson_title}")
        user_state.add_turn(role="model", content=sanitized)

        # Navigation buttons for next lesson
        keyboard = [
            [
                InlineKeyboardButton("📖 មេរៀនបន្ទាប់ ▶", callback_data=f"lesson:{course_key}:{min(100, lesson_num+1)}"),
                InlineKeyboardButton("📚 បញ្ជីមេរៀន", callback_data=f"course:{course_key}:{(lesson_num-1)//10+1}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await query.message.reply_text(sanitized, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        except Exception as e:
            plain_text = re.sub(r"<[^>]+>", "", sanitized)
            await query.message.reply_text(plain_text, reply_markup=reply_markup)


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

    try:
        await update.message.reply_text(sanitized_response, parse_mode=ParseMode.HTML)
    except Exception as e:
        plain_text = re.sub(r"<[^>]+>", "", sanitized_response)
        await update.message.reply_text(plain_text)


def setup_handlers(application: Application) -> None:
    """Registers all command, callback, and message handlers."""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ai", ai_courses_command))
    application.add_handler(CommandHandler("courses", ai_courses_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

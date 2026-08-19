"""Supreme Polymath AI Grandmaster Telegram Bot Launcher."""
import sys
import logging
from telegram import BotCommand
from telegram.ext import Application, ApplicationBuilder

from config import Config
from bot.handlers import setup_handlers

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger("PolymathBot")


from telegram import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

async def post_init(application: Application) -> None:
    """Configures Telegram Bot Commands Menu for regular users and Admin scope."""
    # Regular user menu
    user_commands = [
        BotCommand("ai", "🎓 បើកបញ្ជី AI Master Courses (100 Lessons per AI)"),
        BotCommand("start", "🚀 ចាប់ផ្តើមការសន្ទនា និងស្វាគមន៍ (Start)"),
        BotCommand("help", "💡 មើលការណែនាំ និងសមត្ថភាព AI (Help)"),
        BotCommand("reset", "🔄 លុបប្រវត្តិសន្ទនាចាស់ (Reset Memory)"),
    ]
    await application.bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    # Admin scope menu specifically for Admin ID 859271875
    if Config.ADMIN_CHAT_ID:
        admin_commands = [
            BotCommand("admin", "🎛️ Admin Control Panel (VIP Dashboard)"),
            BotCommand("addvip", "🔑 Grant or Extend VIP License for User"),
            BotCommand("addsupervip", "🌟 Grant or Extend Super VIP License for User"),
            BotCommand("delvip", "🗑️ Revoke VIP/Super VIP License"),
            BotCommand("viplist", "📋 List All Active Licensed Subscriptions"),
            BotCommand("status", "📊 VPS Health, CPU, RAM & Disk Usage"),
            BotCommand("models", "🤖 View Active AI Models & Ollama Engine"),
            BotCommand("vip", "🔔 Toggle VIP User Live Activity Alerts"),
            BotCommand("clearcache", "🧹 Flush Instant Response Cache"),
            BotCommand("broadcast", "📢 Broadcast Announcement to All Users"),
            BotCommand("ai", "🎓 បើកបញ្ជី AI Master Courses"),
            BotCommand("start", "🚀 Re-initialize dialogue"),
            BotCommand("help", "💡 View Grandmaster capabilities"),
            BotCommand("reset", "🔄 Clear memory state"),
        ]


        try:
            await application.bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=Config.ADMIN_CHAT_ID))
            logger.info(f"Registered Admin Command Menu for Admin ID {Config.ADMIN_CHAT_ID} successfully.")
        except Exception as e:
            logger.warning(f"Could not set Admin scope menu for ID {Config.ADMIN_CHAT_ID}: {e}")




def main() -> None:
    """Main entry point to launch the Polymath AI Grandmaster Telegram Bot."""
    logger.info("Initializing Supreme Polymath AI Grandmaster Cognitive System...")

    # Validate Configuration
    warnings = Config.validate()
    if warnings:
        for w in warnings:
            logger.warning(f"CONFIG NOTICE: {w}")

    if not Config.TELEGRAM_BOT_TOKEN or Config.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error(
            "CRITICAL: TELEGRAM_BOT_TOKEN is not configured. "
            "Please set TELEGRAM_BOT_TOKEN in .env file before starting."
        )
        print("\n[!] Please edit the .env file and set your TELEGRAM_BOT_TOKEN and GEMINI_API_KEY.")
        sys.exit(1)

    # Build Telegram Application with post_init
    try:
        application = (
            ApplicationBuilder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            .post_init(post_init)
            .build()
        )
        setup_handlers(application)

        logger.info("Polymath AI Grandmaster Bot is active and polling for incoming queries...")
        application.run_polling()
    except Exception as e:
        logger.critical(f"Failed to launch Telegram Bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

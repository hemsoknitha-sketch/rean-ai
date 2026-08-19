"""Automated Daily 2:00 AM Phnom Penh (+7 ICT) Backup & Disaster Recovery Engine."""
import os
import zipfile
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple


from config import Config

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SCRATCH_BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "backups")


class BackupEngine:
    """Manages creation and Telegram transmission of database backup ZIP archives."""

    @staticmethod
    def create_backup_zip() -> Tuple[str, str, int]:
        """Creates a timestamped ZIP file of all data/*.json files. Returns (zip_path, zip_filename, file_size_bytes)."""
        os.makedirs(SCRATCH_BACKUP_DIR, exist_ok=True)
        
        # Phnom Penh (+7 ICT) Time
        ict_tz = timezone(timedelta(hours=7))
        now_ict = datetime.now(ict_tz)
        timestamp_str = now_ict.strftime("%Y%m%d_%H%M%S")
        zip_filename = f"polymath_backup_{timestamp_str}.zip"
        zip_path = os.path.join(SCRATCH_BACKUP_DIR, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(DATA_DIR):
                for fname in os.listdir(DATA_DIR):
                    if fname.endswith(".json"):
                        file_full_path = os.path.join(DATA_DIR, fname)
                        zipf.write(file_full_path, arcname=fname)

        file_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
        return zip_path, zip_filename, file_size

    @staticmethod
    async def send_backup_to_admin(bot) -> bool:
        """Generates ZIP backup and sends document to Admin chat ID."""
        if not Config.ADMIN_CHAT_ID:
            logger.warning("Cannot send backup: Config.ADMIN_CHAT_ID is missing.")
            return False

        try:
            ict_tz = timezone(timedelta(hours=7))
            now_ict = datetime.now(ict_tz)
            date_str = now_ict.strftime("%Y-%m-%d %H:%M:%S")

            zip_path, zip_filename, file_size = BackupEngine.create_backup_zip()
            size_kb = round(file_size / 1024, 2)

            caption = (
                "📦 <b>AUTOMATED DAILY SYSTEM DATABASE BACKUP</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"📅 <b>កាលបរិច្ឆេទ ៖</b> <code>{date_str}</code> (Phnom Penh ICT +7)\n"
                f"💾 <b>ទំហំឯកសារ ៖</b> <b>{size_kb} KB</b> (ZIP Archive)\n\n"
                "📋 <b>ទិន្នន័យដែលបាន Backup ៖</b>\n"
                "• 👑 VIP & Super VIP Members DB (<code>vip_users.json</code>)\n"
                "• 👤 Registered Free Leads DB (<code>registered_users.json</code>)\n"
                "• 🎓 1,200 AI Masterclasses Cache (<code>lesson_cache.json</code>)\n"
                "• 📖 APEX Khmer Novel Cache (<code>novel_cache.json</code>)\n"
                "• 🔞 Queen of Romance 18+ Cache (<code>novel_18_cache.json</code>)\n"
                "• 💡 AGI Master Prompt Cache (<code>master_prompt_cache.json</code>)\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "🔒 <b>សុវត្ថិភាព ៖</b> ទិន្នន័យត្រូវបានរក្សាទុកមានសុវត្ថិភាព ១០០% គ្មានថ្ងៃបាត់បង់ឡើយ!"
            )

            with open(zip_path, "rb") as document_file:
                await bot.send_document(
                    chat_id=Config.ADMIN_CHAT_ID,
                    document=document_file,
                    filename=zip_filename,
                    caption=caption,
                    parse_mode="HTML"
                )

            logger.info(f"Successfully sent automated backup archive '{zip_filename}' to Admin ID {Config.ADMIN_CHAT_ID}.")
            
            # Clean up local temp zip
            if os.path.exists(zip_path):
                os.remove(zip_path)
            return True

        except Exception as e:
            logger.error(f"Failed to send backup archive to Admin: {e}")
            return False

    @staticmethod
    async def schedule_daily_2am_backup(bot) -> None:
        """Background loop executing daily backup at exactly 02:00 AM Phnom Penh Time (ICT UTC+7)."""
        logger.info("Initialized Automated 2:00 AM Phnom Penh Daily Backup Scheduler Daemon.")
        ict_tz = timezone(timedelta(hours=7))

        while True:
            try:
                now_ict = datetime.now(ict_tz)
                # Target time today at 02:00:00 AM ICT
                target_time = now_ict.replace(hour=2, minute=0, second=0, microsecond=0)
                
                # If 2:00 AM has already passed today, target 2:00 AM tomorrow
                if now_ict >= target_time:
                    target_time += timedelta(days=1)

                seconds_until_2am = (target_time - now_ict).total_seconds()
                logger.info(f"Backup Scheduler: Next automated backup scheduled in {round(seconds_until_2am / 3600, 2)} hours (at {target_time.strftime('%Y-%m-%d %H:%M:%S')} ICT).")
                
                await asyncio.sleep(seconds_until_2am)

                # Trigger backup at 2:00 AM
                logger.info("Triggering 02:00 AM Automated Backup Transmission...")
                await BackupEngine.send_backup_to_admin(bot)

                # Wait 60 seconds after trigger to prevent double execution in same minute
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Error in backup scheduler loop: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes if error

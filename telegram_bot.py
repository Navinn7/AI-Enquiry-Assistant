"""
telegram_bot.py  -  Telegram bot for QuAnHack Enquiry Assistant.
Run with: python telegram_bot.py
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import init_db, SessionLocal
from app.intent_handler import handle_message
from app.followup import schedule_all_followups


# ── Handlers ───────────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    db = SessionLocal()
    try:
        reply = handle_message("hi", chat_id, db)
    finally:
        db.close()
    await update.message.reply_text(reply)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.strip()
    chat_id  = str(update.effective_chat.id)

    print(f"[INBOUND] {chat_id}: {user_msg}")

    db = SessionLocal()
    try:
        reply = handle_message(user_msg, chat_id, db)
    finally:
        db.close()

    print(f"[OUTBOUND] -> {chat_id}: {reply[:80]}...")
    await update.message.reply_text(reply)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    init_db()

    # Preload RAG chain
    from app.rag_chain import rag_chain
    chroma_path = Path(__file__).parent / "chroma_db"
    if chroma_path.exists():
        print("Loading RAG chain, please wait...")
        rag_chain._build()
        print("RAG chain ready!")
    else:
        print("chroma_db not found - run python ingest.py first")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("[ERROR] TELEGRAM_BOT_TOKEN not set in .env")
        return

    # Build Telegram app
    app = Application.builder().token(token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # ── APScheduler setup inside post_init so event loop is running ────────
    async def post_init(application):
        scheduler = AsyncIOScheduler()

        async def check_followups():
            schedule_all_followups(scheduler, application.bot)

        scheduler.add_job(
            check_followups,
            "interval",
            seconds=30,
            id="followup_checker",
        )

        scheduler.start()
        print("Follow-up scheduler started.")
        print(f"Follow-up delay: {os.getenv('FOLLOWUP_SECONDS', '86400')} seconds")

    app.post_init = post_init

    print("\nBot is running! Open Telegram and message your bot.")
    print("Press CTRL+C to stop.\n")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
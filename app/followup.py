"""
followup.py  -  APScheduler-based follow-up message sender.
Runs inside telegram_bot.py process. No Redis or Celery needed.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

FOLLOWUP_SECONDS = int(os.getenv("FOLLOWUP_SECONDS", "86400"))

FOLLOWUP_MESSAGE = (
    "Hi {name}! This is a follow-up from QuAnHack Academy.\n\n"
    "Has our admissions team reached out to you yet?\n\n"
    "Reply YES if you heard from us or NO if you haven't "
    "and we will make sure someone contacts you shortly."
)

YES_RESPONSE = (
    "Great! We are glad our team reached out. "
    "Feel free to ask anything else about our courses anytime!"
)

NO_RESPONSE = (
    "We are sorry about that! We have noted this and our team "
    "will contact you within the next few hours. "
    "Thank you for your patience!"
)

# Track who is waiting for a YES/NO followup reply
# { telegram_id: True }
pending_followup_replies: dict[str, bool] = {}


def is_followup_reply(phone: str) -> bool:
    return str(phone) in pending_followup_replies


def handle_followup_reply(message: str, phone: str) -> str:
    msg = message.strip().lower()
    phone = str(phone)

    if msg in ("yes", "y", "yeah", "yep"):
        pending_followup_replies.pop(phone, None)
        return YES_RESPONSE

    elif msg in ("no", "n", "nope", "not yet"):
        pending_followup_replies.pop(phone, None)
        return NO_RESPONSE

    else:
        return (
            "Please reply YES if our team has contacted you "
            "or NO if they haven't."
        )


async def send_followup(telegram_id: str, name: str, bot):
    """Send the follow-up message to a user via Telegram."""
    try:
        message = FOLLOWUP_MESSAGE.format(name=name)
        await bot.send_message(chat_id=int(telegram_id), text=message)

        # Mark as sent in Excel
        from app.leads_export import mark_followup_sent
        mark_followup_sent(telegram_id)

        # Track that we are waiting for their YES/NO reply
        pending_followup_replies[str(telegram_id)] = True

        print(f"[FOLLOWUP] Sent to {telegram_id} ({name})")

    except Exception as e:
        print(f"[FOLLOWUP ERROR] {telegram_id}: {e}")


def schedule_all_followups(scheduler, bot):
    """
    Called once at startup and then every minute by APScheduler.
    Checks Excel for leads with Follow Up Sent = No and schedules them.
    """
    from app.leads_export import get_pending_followups
    import asyncio

    pending = get_pending_followups()

    for lead in pending:
        telegram_id = lead["telegram_id"]
        name        = lead["name"]
        timestamp   = lead["timestamp"]

        # Parse the lead timestamp
        try:
            if isinstance(timestamp, str):
                lead_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            else:
                lead_time = timestamp
        except Exception:
            continue

        # Calculate when to send the follow-up
        send_at = lead_time + timedelta(seconds=FOLLOWUP_SECONDS)
        now     = datetime.now()

        job_id = f"followup_{telegram_id}"

        # Skip if already scheduled
        if scheduler.get_job(job_id):
            continue

        if send_at <= now:
            # Overdue — send immediately
            scheduler.add_job(
                send_followup,
                "date",
                run_date=now,
                args=[telegram_id, name, bot],
                id=job_id,
            )
            print(f"[SCHEDULER] Immediate follow-up queued for {name} ({telegram_id})")
        else:
            # Schedule for future
            scheduler.add_job(
                send_followup,
                "date",
                run_date=send_at,
                args=[telegram_id, name, bot],
                id=job_id,
            )
            seconds_left = (send_at - now).seconds
            print(f"[SCHEDULER] Follow-up for {name} in {seconds_left}s at {send_at}")
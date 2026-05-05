"""
test_local.py  –  Test the bot locally via terminal WITHOUT WhatsApp or Twilio.

Usage:
    python test_local.py

Type any message and press Enter. Type 'quit' to exit.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.database import init_db, SessionLocal
from app.intent_handler import handle_message

TEST_PHONE = "whatsapp:+910000000000"

def main():
    init_db()
    db = SessionLocal()

    # Preload RAG so first reply is instant
    from app.rag_chain import rag_chain
    from pathlib import Path
    if (Path(__file__).parent.parent / "chroma_db").exists():
        print("⏳ Loading RAG chain, please wait...")
        rag_chain._build()
        print("✅ Ready! Start chatting.\n")
    print("=" * 55)
    print("  QuAnHack Enquiry Bot – Local Test Console")
    print("  Type your message and press Enter.")
    print("  Type 'quit' to exit.")
    print("=" * 55)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Exiting]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        reply = handle_message(user_input, TEST_PHONE, db)
        print(f"\nBot: {reply}\n")

    db.close()


if __name__ == "__main__":
    main()

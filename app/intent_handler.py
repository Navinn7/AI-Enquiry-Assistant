"""
intent_handler.py  –  Routes an incoming WhatsApp message to the right handler.

Intent priority:
  1. In active lead-capture flow  →  handle next step
  2. Trigger keyword detected     →  start lead capture
  3. Greeting                     →  welcome message
  4. Everything else              →  RAG answer
"""

import os
from .followup import is_followup_reply, handle_followup_reply
from sqlalchemy.orm import Session
from .lead_flow import is_in_lead_flow, is_trigger, start_lead_flow, handle_lead_step
from .rag_chain import ask_rag


INSTITUTION = os.getenv("INSTITUTION_NAME", "Our Academy")

GREETING_KEYWORDS = ["hi", "hello", "hey", "helo", "hii", "good morning",
                     "good afternoon", "good evening", "start", "help"]

WELCOME_MESSAGE = (
    f"👋 Hello! Welcome to {INSTITUTION} Admissions Assistant.\n\n"
    "I can help you with:\n"
    "• 📚 Course details & curriculum\n"
    "• 💰 Fees & payment options\n"
    "• 📅 Batch schedules & timings\n"
    "• ✅ Eligibility criteria\n"
    "• 📝 Enrollment process\n\n"
    "Just ask me anything, or type enroll to speak with our admissions team!"
)


CASUAL_KEYWORDS = [
    "thanks", "thank you", "thankyou", "thx", "ok", "okay", "alright",
    "got it", "understood", "sure", "great", "nice", "cool", "awesome",
    "perfect", "bye", "goodbye", "see you", "take care", "noted",
    "sounds good", "that helps", "helpful", "good", "fine", "yes", "no",
    "hmm", "oh", "wow", "interesting", "i see", "makes sense"
]

CASUAL_RESPONSES = {
    "thanks": "You are welcome! Let me know if you have any other questions about our courses.",
    "thank you": "You are welcome! Feel free to ask anything about our programs.",
    "bye": "Goodbye! Feel free to come back anytime. We are here to help.",
    "goodbye": "Goodbye! Best of luck with your learning journey.",
    "ok": "Sure! Let me know if you need anything else about our courses.",
    "okay": "Sure! Let me know if you need anything else about our courses.",
    "got it": "Great! Let me know if you have more questions.",
    "understood": "Great! Feel free to ask anything else about our programs.",
    "yes": "Sure! What would you like to know about our courses?",
    "no": "No problem! Let me know if you need anything else.",
    "great": "Glad to hear that! Let me know if you have more questions.",
    "awesome": "Glad to hear that! Feel free to ask anything else.",
    "perfect": "Glad to hear that! Let me know if you need more information.",
    "sounds good": "Glad to hear that! Feel free to ask anything else.",
    "that helps": "Happy to help! Let me know if you have more questions.",
    "helpful": "Happy to help! Feel free to ask anything else.",
}

DEFAULT_CASUAL_RESPONSE = "Sure! Let me know if you have any questions about our courses, fees, or admissions."


def is_casual(message: str) -> bool:
    msg = message.lower().strip()
    return any(msg == kw or msg.startswith(kw) for kw in CASUAL_KEYWORDS)


def get_casual_response(message: str) -> str:
    msg = message.lower().strip()
    for kw, response in CASUAL_RESPONSES.items():
        if msg == kw or msg.startswith(kw):
            return response
    return DEFAULT_CASUAL_RESPONSE


def handle_message(message: str, phone: str, db: Session) -> str:
    msg = message.strip()
    msg_lower = msg.lower()

    # 0. Follow-up reply — highest priority
    if is_followup_reply(phone):
        return handle_followup_reply(msg, phone)

    # 1. Active lead-capture flow
    if is_in_lead_flow(phone, db):
        return handle_lead_step(msg, phone, db)

    # 2. Enrollment trigger
    if is_trigger(msg_lower):
        return start_lead_flow(phone, db)

    # 3. Greeting
    if any(msg_lower.startswith(g) for g in GREETING_KEYWORDS) and len(msg) < 30:
        return WELCOME_MESSAGE

    # 4. Casual
    if is_casual(msg_lower):
        return get_casual_response(msg_lower)

    # 5. RAG
    return ask_rag(msg, phone)

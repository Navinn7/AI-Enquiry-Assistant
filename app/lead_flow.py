"""
lead_flow.py  –  Multi-step WhatsApp conversation for capturing lead details.
"""

import os
from sqlalchemy.orm import Session
from .database import ConversationState

TRIGGER_KEYWORDS = [
    "enroll", "enrol", "register", "apply", "admission",
    "contact", "call me", "speak", "talk", "join",
    "interested", "sign up", "signup",
]

INSTITUTION = os.getenv("INSTITUTION_NAME", "Our Academy")


def get_state(phone: str, db: Session):
    return db.query(ConversationState).filter(
        ConversationState.phone == phone
    ).first()


def set_state(phone: str, step: str, db: Session, **kwargs):
    state = get_state(phone, db)
    if not state:
        state = ConversationState(phone=phone)
        db.add(state)
    state.step = step
    for k, v in kwargs.items():
        setattr(state, k, v)
    db.commit()


def clear_state(phone: str, db: Session):
    state = get_state(phone, db)
    if state:
        db.delete(state)
        db.commit()


def is_trigger(message: str) -> bool:
    msg = message.lower()
    return any(kw in msg for kw in TRIGGER_KEYWORDS)


def is_in_lead_flow(phone: str, db: Session) -> bool:
    state = get_state(phone, db)
    return state is not None and state.step not in ("none", "done")


def start_lead_flow(phone: str, db: Session) -> str:
    set_state(phone, "name", db)
    return (
        f"Great! I would love to connect you with our admissions team at {INSTITUTION}.😊\n\n"
        "First, could you share your full name?"
    )


def _build_confirmation(state) -> str:
    return (
        "Please confirm your details:\n\n"
        f"Name: {state.name}\n"
        f"Phone Number: {state.user_phone}\n"
        f"Email: {state.email}\n"
        f"Course Interest: {state.interest}\n\n"
        "Is this correct? Reply yes to confirm or no to re-enter your details.✅"
    )


def handle_lead_step(message: str, phone: str, db: Session) -> str:
    state = get_state(phone, db)
    if not state:
        return start_lead_flow(phone, db)

    step = state.step
    msg  = message.strip()

    # Step 1 — collect name
    if step == "name":
        if len(msg) < 2:
            return "Please enter your full name."
        set_state(phone, "user_phone", db, name=msg)
        return (
            f"Nice to meet you, {msg}!👋\n\n"
            "Could you share your phone number so our team can reach you?"
        )

    # Step 2 — collect phone number
    elif step == "user_phone":
        digits = "".join(filter(str.isdigit, msg))
        if len(digits) < 10:
            return "Please enter a valid phone number with at least 10 digits."
        set_state(phone, "email", db, user_phone=msg)
        return "Got it! Now could you share your email address?📧"

    # Step 3 — collect email
    elif step == "email":
        if "@" not in msg or "." not in msg:
            return "That does not look like a valid email. Please re-enter it. (e.g. yourname@gmail.com)"
        set_state(phone, "interest", db, email=msg)
        return (
            "Almost done! Which course or program are you interested in?🎯\n"
            "(e.g. Python, Data Science and ML, Full Stack, AI and Prompt Engineering, Cybersecurity...)"
        )

    # Step 4 — collect course interest
    elif step == "interest":
        set_state(phone, "confirm", db, interest=msg)
        state = get_state(phone, db)
        return _build_confirmation(state)

    # Step 5 — confirmation
    elif step == "confirm":
        msg_lower = msg.lower().strip()

        if msg_lower in ("yes", "y", "yeah", "yep", "correct", "confirm", "ok", "okay"):
            state = get_state(phone, db)

            # Save to Excel
            from .leads_export import save_to_excel
            save_to_excel(
                telegram_id=phone,
                name=state.name,
                interest=state.interest,
                email=state.email,
                user_phone=state.user_phone,
            )

            clear_state(phone, db)

            return (
                f"Thank you, {state.name}!🙌\n\n"
                f"Your interest in {state.interest} has been recorded.\n"
                "Our admissions team will reach out to you within 24 hours.\n\n"
                "Feel free to ask me anything else about our courses!"
            )

        elif msg_lower in ("no", "n", "nope", "wrong", "incorrect"):
            # Restart the flow
            clear_state(phone, db)
            set_state(phone, "name", db)
            return (
                "No problem! Let us start over.🔄️\n\n"
                "Could you share your full name?"
            )

        else:
            # Did not understand the confirmation response
            state = get_state(phone, db)
            return (
                "Please reply yes to confirm or no to re-enter your details.\n\n"
                + _build_confirmation(state)
            )

    clear_state(phone, db)
    return "Something went wrong. Let us start over — what would you like to know?"
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal

from app.core.db import get_db
from app.core.security import require_user
from app.models.ticket import Ticket
from app.models.ticket_message import TicketMessage

router = APIRouter()


class DraftReplyIn(BaseModel):
    ticket_id: int
    tone: Literal["friendly", "professional", "short"] = "friendly"


class DraftReplyOut(BaseModel):
    draft: str


@router.post("/draft-reply", response_model=DraftReplyOut)
def draft_reply(payload: DraftReplyIn, db: Session = Depends(get_db), user=Depends(require_user)):
    ticket = db.query(Ticket).filter(Ticket.id == payload.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="ticket not found")

    msgs = (
        db.query(TicketMessage)
        .filter(TicketMessage.ticket_id == payload.ticket_id)
        .order_by(TicketMessage.id.asc())
        .all()
    )

    last_user = None
    for m in reversed(msgs):
        if m.author_type == "user":
            last_user = m.body
            break

    if not last_user:
        last_user = "Customer asked for help."

    if payload.tone == "short":
        draft = f"Thanks for reaching out. We’re looking into it and will get back to you soon.\n\nRef: {ticket.subject}"
    elif payload.tone == "professional":
        draft = (
            f"Hello,\n\nThank you for contacting support regarding: {ticket.subject}.\n"
            f"We’ve received your message and will investigate.\n\n"
            f"Last message: {last_user}\n\nBest regards,\nSupport Team"
        )
    else:
        draft = (
            f"Hey! Thanks for reaching out 💙\n\n"
            f"I saw your message about “{ticket.subject}”.\n"
            f"Last thing you said: {last_user}\n\n"
            f"I’m on it and I’ll update you soon."
        )

    return {"draft": draft}

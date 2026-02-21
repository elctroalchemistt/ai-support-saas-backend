from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.orm import Session, selectinload

from app.core.db import get_db
from app.core.security import get_current_user_from_request
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.ticket_message import TicketMessage, MessageRole

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TicketCreateIn(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=1, max_length=5000)
    priority: TicketPriority = TicketPriority.medium


class TicketOut(BaseModel):
    id: int
    org_id: int
    subject: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: int
    ticket_id: int
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketDetailOut(TicketOut):
    messages: List[MessageOut]


class AddMessageIn(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    role: MessageRole = MessageRole.user


class TicketUpdateIn(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    subject: str | None = Field(default=None, min_length=3, max_length=200)


def _require_org_user(request: Request, db: Session):
    user = get_current_user_from_request(request, db)
    org_id = getattr(user, "org_id", None)
    if not org_id:
        raise HTTPException(status_code=400, detail="User has no org_id assigned")
    return user, org_id


@router.post("", response_model=TicketOut)
def create_ticket(payload: TicketCreateIn, request: Request, db: Session = Depends(get_db)):
    _, org_id = _require_org_user(request, db)
    now = _utcnow()

    t = Ticket(
        org_id=org_id,
        subject=payload.subject,
        status=TicketStatus.open,
        priority=payload.priority,
        created_at=now,
        updated_at=now,
    )
    db.add(t)
    db.flush()

    m = TicketMessage(
        ticket_id=t.id,
        role=MessageRole.user,
        content=payload.message,
        created_at=now,
    )
    db.add(m)
    db.commit()
    db.refresh(t)
    return t


@router.get("", response_model=List[TicketOut])
def list_tickets(request: Request, db: Session = Depends(get_db), limit: int = 20, offset: int = 0):
    _, org_id = _require_org_user(request, db)

    q = (
        select(Ticket)
        .where(Ticket.org_id == org_id)
        .order_by(desc(Ticket.updated_at))
        .limit(min(max(limit, 1), 100))
        .offset(max(offset, 0))
    )
    return list(db.scalars(q).all())


@router.get("/{ticket_id}", response_model=TicketDetailOut)
def get_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    _, org_id = _require_org_user(request, db)

    q = (
        select(Ticket)
        .where(Ticket.id == ticket_id, Ticket.org_id == org_id)
        .options(selectinload(Ticket.messages))
    )
    t = db.scalar(q)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return t


@router.post("/{ticket_id}/messages", response_model=MessageOut)
def add_message(ticket_id: int, payload: AddMessageIn, request: Request, db: Session = Depends(get_db)):
    _, org_id = _require_org_user(request, db)

    t = db.scalar(select(Ticket).where(Ticket.id == ticket_id, Ticket.org_id == org_id))
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")

    now = _utcnow()
    msg = TicketMessage(
        ticket_id=t.id,
        role=payload.role,
        content=payload.content,
        created_at=now,
    )
    t.updated_at = now

    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, payload: TicketUpdateIn, request: Request, db: Session = Depends(get_db)):
    _, org_id = _require_org_user(request, db)

    t = db.scalar(select(Ticket).where(Ticket.id == ticket_id, Ticket.org_id == org_id))
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")

    changed = False
    if payload.subject is not None:
        t.subject = payload.subject
        changed = True
    if payload.status is not None:
        t.status = payload.status
        changed = True
    if payload.priority is not None:
        t.priority = payload.priority
        changed = True

    if changed:
        t.updated_at = _utcnow()
        db.commit()
        db.refresh(t)

    return t

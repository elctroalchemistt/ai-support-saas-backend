from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.models.kb import KBArticle
from app.schemas.kb import KBCreateIn
from app.routers._deps import get_current_user

router = APIRouter()

def _tags_to_csv(tags: list[str]) -> str:
    clean = []
    for t in tags:
        x = (t or "").strip()
        if x:
            clean.append(x)
    return ",".join(clean)

def _csv_to_tags(s: str) -> list[str]:
    if not s:
        return []
    return [x for x in (p.strip() for p in s.split(",")) if x]

@router.post("")
def create_article(payload: KBCreateIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    a = KBArticle(title=payload.title.strip(), body=payload.body, tags_csv=_tags_to_csv(payload.tags))
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id, "title": a.title, "body": a.body, "tags": _csv_to_tags(a.tags_csv)}

@router.get("")
def list_articles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = db.scalars(select(KBArticle).order_by(KBArticle.id.desc())).all()
    return {"items": [{"id": a.id, "title": a.title, "body": a.body, "tags": _csv_to_tags(a.tags_csv)} for a in items]}

@router.get("/search")
def search(q: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q2 = f"%{q.strip()}%"
    items = db.scalars(select(KBArticle).where(KBArticle.title.ilike(q2)).order_by(KBArticle.id.desc())).all()
    return {"items": [{"id": a.id, "title": a.title, "body": a.body, "tags": _csv_to_tags(a.tags_csv)} for a in items]}

@router.get("/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    a = db.scalar(select(KBArticle).where(KBArticle.id == article_id))
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"id": a.id, "title": a.title, "body": a.body, "tags": _csv_to_tags(a.tags_csv)}

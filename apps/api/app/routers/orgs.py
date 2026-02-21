from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.db import get_db
from app.core.security import require_user
from app.models.org import Org

router = APIRouter(prefix="/orgs", tags=["orgs"])


class OrgCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class OrgOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


@router.get("", response_model=dict)
def list_orgs(db: Session = Depends(get_db), user=Depends(require_user)):
    items = db.query(Org).order_by(Org.id.desc()).all()
    return {"items": items}


@router.post("", response_model=OrgOut)
def create_org(payload: OrgCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    existing = db.query(Org).filter(Org.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Org name already exists")

    org = Org(name=payload.name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

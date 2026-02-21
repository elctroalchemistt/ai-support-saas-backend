from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user_from_request, require_roles
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    return get_current_user_from_request(request, db)


def require_org_user(user: User = Depends(get_current_user)) -> User:
    if not getattr(user, "org_id", None):
        raise HTTPException(status_code=403, detail="User has no org")
    return user


def require_admin(user: User = Depends(require_org_user)) -> User:
    require_roles(user, roles=["owner", "admin"])
    return user

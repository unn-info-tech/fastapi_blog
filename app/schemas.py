from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ─── POST SCHEMAS ─────────────────────────────

class PostBase(BaseModel):
    title: str              # post title
    content: str            # post content
    published: bool = True  # default = True

class PostCreate(PostBase):
    pass  # used when creating a post (same fields as base)

class PostUpdate(PostBase):
    pass  # used when updating a post (same fields)

class PostResponse(PostBase):
    id: int                 # comes from DB
    created_at: datetime    # timestamp from DB
    owner_id: Optional[int] = None  # may be None

    class Config:
        from_attributes = True  # allows reading from ORM (DB model)

# ─── USER SCHEMAS ─────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr   # automatically checks valid email
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # ORM → schema conversion
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ─── POST SCHEMAS ─────────────────────────────

class PostBase(BaseModel):
    title: str              # post title
    content: str            # post content
    published: bool = True  # default = True
    category_id: Optional[int] = None  # optional category association
    owner_id: Optional[int] = None  # optional owner association

class PostCreate(PostBase):
    pass  # used when creating a post (same fields as base)

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
    category_id: Optional[int] = None
    owner_id: Optional[int] = None

class PostResponse(PostBase):
    id: int                 # comes from DB
    created_at: datetime    # timestamp from DB
    owner_id: Optional[int] = None  # may be None
    category_id: Optional[int] = None  # may be None

    class Config:
        from_attributes = True  # allows reading from ORM (DB model)

# ─── POST WITH OWNER ───────────────────────────
class PostWithOwner(PostResponse):
    owner: Optional['UserResponse'] = None

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

# ─── CATEGORY SCHEMAS ─────────────────────────────

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
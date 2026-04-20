from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ─── POST SCHEMAS ─────────────────────────────

class PostBase(BaseModel):
    title: str              # post title
    content: str            # post content
    published: bool = True  # default = True
    rating: Optional[int] = None 

class PostCreate(PostBase):
    pass  # used when creating a post (same fields as base)

class PostUpdate(PostBase):
    pass  # used when updating a post (same fields)

class OwnerInfo(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: Optional[int] = None
    owner: Optional[OwnerInfo] = None   # ← YANGI

    class Config:
        from_attributes = True

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



from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ... (avvalgi schemalar)

# ─── TOKEN SCHEMAS ────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None




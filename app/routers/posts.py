from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# ─── CREATE ───────────────────────────────────
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PostResponse
)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)   # DB dan yangi ma'lumotni olish (id, created_at)
    return new_post

# ─── READ ALL ─────────────────────────────────
from typing import List, Optional

# ─── READ ALL (qidiruv + pagination) ─────────
@router.get(
    "/",
    response_model=List[schemas.PostResponse]
)
def get_all_posts(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    posts = db.query(models.Post).filter(
        models.Post.title.contains(search)
    ).limit(limit).offset(skip).all()

    return posts

# ─── READ ONE ─────────────────────────────────
@router.get(
    "/{post_id}",
    response_model=schemas.PostWithOwner
)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={post_id} bo'lgan post topilmadi"
        )

    return post

# ─── UPDATE ───────────────────────────────────
@router.put(
    "/{post_id}",
    response_model=schemas.PostResponse
)
def update_post(
    post_id: int,
    updated_post: schemas.PostUpdate,
    db: Session = Depends(get_db)
):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={post_id} bo'lgan post topilmadi"
        )

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()

# ─── PARTIAL UPDATE (PATCH) ───────────────────
@router.patch(
    "/{post_id}",
    response_model=schemas.PostResponse
)
def partial_update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db)
):
    # Faqat berilgan maydonlarni yangilash
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    if not post_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post topilmadi"
        )
    post_query.update(post.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return post_query.first()

# ─── DELETE ───────────────────────────────────
@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={post_id} bo'lgan post topilmadi"
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return None


@router.get("/user/{user_id}/posts", response_model=List[schemas.PostResponse])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(
        models.Post.owner_id == user_id
    ).all()
    return posts



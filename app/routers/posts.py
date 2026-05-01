from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from .. import models, schemas, oauth2
from ..database import get_db
from ..cache import cache_get, cache_set, cache_delete, cache_delete_pattern
from fastapi import Request
from ..middleware.rate_limit import rate_limit_middleware
router = APIRouter(prefix="/posts", tags=["Posts"])

# ─── READ ALL (cache bilan) ───────────────────
@router.get(
    "/",
    response_model=List[schemas.PostResponse]
)
async def get_all_posts(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    
    # Postlarga yumshoq cheklash: 100 ta/daqiqa
    await rate_limit_middleware(request, calls=100, period=60)

    # Cache kaliti (parametrlar bilan)
    cache_key = f"posts:all:limit={limit}:skip={skip}:search={search}"

    # 1. Cache dan tekshirish
    cached = cache_get(cache_key)
    if cached:
        print(f"✅ Cache HIT: {cache_key}")
        return cached

    # 2. Cache Miss → DB dan olish
    print(f"❌ Cache MISS: {cache_key}")
    posts = db.query(models.Post).filter(
        models.Post.title.contains(search)
    ).limit(limit).offset(skip).all()

    # SQLAlchemy → Dict ga aylantirish
    posts_data = [
        schemas.PostResponse.from_orm(p).dict()
        for p in posts
    ]

    # 3. Cache ga saqlash (5 daqiqa)
    cache_set(cache_key, posts_data, ttl=300)

    return posts


# ─── READ ONE (cache bilan) ───────────────────
@router.get(
    "/{post_id}",
    response_model=schemas.PostResponse
)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    cache_key = f"posts:{post_id}"

    # Cache tekshirish
    cached = cache_get(cache_key)
    if cached:
        print(f"✅ Cache HIT: {cache_key}")
        return cached

    print(f"❌ Cache MISS: {cache_key}")
    post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={post_id} bo'lgan post topilmadi"
        )

    post_data = schemas.PostResponse.from_orm(post).dict()

    # Cache ga saqlash (10 daqiqa)
    cache_set(cache_key, post_data, ttl=600)

    return post


# ─── CREATE (cache tozalash) ──────────────────
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PostResponse
)
async def create_post(
    post: schemas.PostCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_post = models.Post(
        owner_id=current_user.id,
        **post.dict()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # Yangi post → Barcha list cache eskirdi → O'chirish
    background_tasks.add_task(
        cache_delete_pattern,
        "posts:all:*"
    )

    return new_post


# ─── UPDATE (cache yangilash) ─────────────────
@router.put(
    "/{post_id}",
    response_model=schemas.PostResponse
)
async def update_post(
    post_id: int,
    updated_post: schemas.PostUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(
        models.Post.id == post_id
    )
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={post_id} bo'lgan post topilmadi"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz bu postni yangilay olmaysiz"
        )

    post_query.update(
        updated_post.dict(),
        synchronize_session=False
    )
    db.commit()

    # Cache tozalash (fonda)
    background_tasks.add_task(cache_delete, f"posts:{post_id}")
    background_tasks.add_task(cache_delete_pattern, "posts:all:*")

    return post_query.first()


# ─── DELETE (cache tozalash) ──────────────────
@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(
        models.Post.id == post_id
    )
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={post_id} bo'lgan post topilmadi"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz bu postni o'chira olmaysiz"
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    # Cache tozalash (fonda)
    background_tasks.add_task(cache_delete, f"posts:{post_id}")
    background_tasks.add_task(cache_delete_pattern, "posts:all:*")

    return None
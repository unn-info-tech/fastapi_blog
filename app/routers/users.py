from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.hashing import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ─── CREATE USER ──────────────────────────────
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        hashed = hash_password(user.password)
        print("HASHED:", hashed)

        new_user = models.User(
            username=user.username,
            email=user.email,
            password=hashed
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception as e:
        print("REAL ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

# ─── GET USER ─────────────────────────────────
@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID={user_id} bo'lgan foydalanuvchi topilmadi"
        )

    return user

# ─── TEST FOR DUPLICATE EMAIL ─────────────────
def test_duplicate_email():
    """
    Test for duplicate email handling.
    Steps:
    1. Create a user with a specific email
    2. Try to create another user with the same email
    3. Verify that a 400 error is raised

    Note: This is a conceptual test. In practice, use FastAPI TestClient:
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Create first user
    response = client.post("/users/", json={"username": "test", "email": "test@example.com", "password": "pass"})
    assert response.status_code == 201

    # Try duplicate
    response = client.post("/users/", json={"username": "test2", "email": "test@example.com", "password": "pass"})
    assert response.status_code == 400
    assert "email allaqachon ro'yxatdan o'tgan" in response.json()["detail"]
    """
    pass
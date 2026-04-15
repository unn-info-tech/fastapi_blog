from fastapi import FastAPI
from .database import engine
from . import models
from .routers import posts, users, categories

# Jadvallarni yaratish
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog API",
    description="FastAPI + PostgreSQL + SQLAlchemy",
    version="2.0.0"
)

# Routerlarni ulash
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(categories.router)

@app.get("/")
def root():
    return {"xabar": "Blog API ga xush kelibsiz! v2.0"}
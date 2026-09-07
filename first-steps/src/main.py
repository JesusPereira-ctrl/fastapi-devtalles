from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.v1.auth.router import router as auth_router
from src.api.v1.posts.router import router as post_router
from src.api.v1.uploads.router import router as upload_router
from src.core.db import Base, engine

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)  # dev

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router, prefix="/api/v1")
    app.include_router(upload_router, prefix="/api/v1")

    return app


app = create_app()

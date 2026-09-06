from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.v1.posts.router import router as post_router
from src.core.db import Base, engine

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)  # dev

    app.include_router(post_router)

    return app


app = create_app()

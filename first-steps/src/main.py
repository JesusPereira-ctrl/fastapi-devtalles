from fastapi import FastAPI
from src.core.db import Base, engine
from dotenv import load_dotenv
from src.api.v1.posts.router import router as post_router
from src.api.v1.welcome.router import router as welcome_router

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title='Mini Blog')
    Base.metadata.create_all(bind=engine)  # dev

    app.include_router(post_router)
    app.include_router(welcome_router)

    return app


app = create_app()

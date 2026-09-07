from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Tag(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=30, description="Nombre de la etiqueta"
    )

    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    tags: list[Tag] | None = Field(default_factory=list)  # []
    author: Author | None = None

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (mínimo 3 caracteres y máximo 100)",
        examples=["Mi primer post con FastAPI"],
    )
    content: str | None = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (mínimo 10 caracteres)",
        examples=["Este es un contenido válido porque tiene 10 caracteres o más"],
    )
    tags: list[Tag] = Field(default_factory=list)  # []

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El titulo no puede contener la palabra: 'spam'")
        return value


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100)
    content: str | None = None  # Optional[str] es equivalente a str | None


class PostPublic(PostBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: str | None = None
    items: list[PostPublic]

from datetime import datetime, timezone
from fastapi import FastAPI, Query, HTTPException, Path, status, Depends
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional, List, Union, Literal
from math import ceil
from sqlalchemy import Integer, String, Text, DateTime, select, func, UniqueConstraint, ForeignKey, Table, Column
from sqlalchemy.orm import Session,  Mapped, mapped_column, relationship, selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from dotenv import load_dotenv

load_dotenv()


Base.metadata.create_all(bind=engine)  # dev


app = FastAPI(title='Mini Blog')


class Tag(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description='Nombre de la etiqueta'
    )

    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    author: Optional[Author] = None

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description='Titulo del post (mínimo 3 caracteres y máximo 100)',
        examples=['Mi primer post con FastAPI']
    )
    content: Optional[str] = Field(
        default='Contenido no disponible',
        min_length=10,
        description='Contenido del post (mínimo 10 caracteres)',
        examples=['Este es un contenido válido porque tiene 10 caracteres o más']
    )
    tags: List[Tag] = Field(default_factory=list)  # []
    author: Optional[Author] = None

    @field_validator('title')
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if 'spam' in value.lower():
            raise ValueError(
                'El titulo no puede contener la palabra: \'spam\''
            )
        return value


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None  # Optional[str] es equivalente a str | None


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
    order_by: Literal['id', 'title']
    direction: Literal['asc', 'desc']
    search: Optional[str] = None
    items: List[PostPublic]


@app.get('/')
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}


@app.get('/posts', response_model=PaginatedPost)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description='Parámetro obsoleto, usa \'query o search\' en su lugar.'
    ),
    query: Optional[str] = Query(
        default=None,
        description='Texto para buscar por título',
        alias='search',
        min_length=3,
        max_length=50,
        pattern=r'^[\w\sáéíóúÁÉÍÓÚüÜ-]+$'
    ),
    per_page: int = Query(
        default=10,
        ge=1,
        le=50,
        description='Número de resultados (1-50)'
    ),
    page: int = Query(
        default=1,
        ge=1,
        description='Número de página (>=1)'
    ),
    order_by: Literal['id', 'title'] = Query(
        default='id',
        description='Campo de orden'
    ),
    direction: Literal['asc', 'desc'] = Query(
        default='asc',
        description='Dirección de orden'
    ),
    db: Session = Depends(get_db)
):
    results = select(PostORM)

    query = query or text

    if query:
        results = results.where(PostORM.title.ilike(f'%{query}%'))

    total = db.scalar(
        select(func.count()).select_from(
            results.subquery()
        )
    ) or 0
    total_pages = ceil(total / per_page) if total > 0 else 0

    current_page = 1 if total_pages == 0 else min(page, total_pages)

    if order_by == 'id':
        order_col = PostORM.id
    else:
        order_col = func.lower(PostORM.title)

    results = results.order_by(
        order_col.asc() if direction == 'asc' else order_col.desc()
    )

    if total_pages == 0:
        items: List[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        items = db.execute(
            results.limit(per_page).offset(start)
        ).scalars().all()

    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )


@app.get('/posts/by-tags', response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description='Una o mas etiquetas. Ejemplo: ?tags=python&tags=fastapi'
    ),
    db: Session = Depends(get_db)
):
    normalized_tag_names = [
        tag.strip().lower()
        for tag in tags
        if tag.strip()
    ]

    if not normalized_tag_names:
        return []

    post_list = (
        select(PostORM)
        .options(
            selectinload(PostORM.tags),
            joinedload(PostORM.author)
        ).where(
            PostORM.tags.any(
                func.lower(TagORM.name).in_(normalized_tag_names)
            )
        ).order_by(
            PostORM.id.asc()
        )
    )

    posts = db.execute(post_list).scalars().all()

    return posts


@app.get('/posts/{post_id}', response_model=Union[PostPublic, PostSummary], response_description='Post encontrado')
def get_post(
    post_id: int = Path(
        ...,
        ge=1,
        title='ID del post',
        description='Identificador entero del post, Debe ser mayor a 1',
        examples=[1]
    ),
    include_content: bool = Query(
        default=True,
        description='Incluir o no el contenido'
    ),
    db: Session = Depends(get_db)
):
    post_find = select(PostORM).where(PostORM.id == post_id)
    post = db.execute(post_find).scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail='Post no encontrado')

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@app.post('/posts', response_model=PostPublic, response_description='Post creado (OK)', status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    author_obj = None
    if post.author:
        author_obj = db.execute(
            select(AuthorORM).where(AuthorORM.email == post.author.email)
        ).scalar_one_or_none()

        if not author_obj:
            author_obj = AuthorORM(
                name=post.author.name,
                email=post.author.email
            )
            db.add(author_obj)
            db.flush()

    new_post = PostORM(
        title=post.title,
        content=post.content,
        author=author_obj
    )

    for tag in post.tags:
        tag_obj = db.execute(
            select(TagORM).where(TagORM.name.ilike(tag.name))
        ).scalar_one_or_none()
        if not tag_obj:
            tag_obj = TagORM(name=tag.name)
            db.add(tag_obj)
            db.flush()
        new_post.tags.append(tag_obj)

    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail='El titulo ya existe, prueba con otro'
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail='Error al crear el post'
        )


@app.put('/posts/{post_id}', response_model=PostPublic, response_description='Post actualizado', response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail='Post no encontrado')

    updates = data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(post, key, value)

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@app.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail='Post no encontrado')

    db.delete(post)
    db.commit()

    return

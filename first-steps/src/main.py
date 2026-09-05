import os
from datetime import datetime, timezone
from fastapi import FastAPI, Query, HTTPException, Path, status, Depends
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional, List, Union, Literal
from math import ceil
from sqlalchemy import create_engine, Integer, String, Text, DateTime, select, func
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./blog.db')
print('Conectado a:', DATABASE_URL)

engine_kwargs = {}

if DATABASE_URL.startswith('sqlite'):
    engine_kwargs['connect_args'] = {'check_same_thread': False}

engine = create_engine(
    url=DATABASE_URL,
    echo=True,
    future=True,
    **engine_kwargs
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session
)


class Base(DeclarativeBase):
    pass


class PostORM(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc)
    )


Base.metadata.create_all(bind=engine)  # dev


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title='Mini Blog')

BLOG_POST = [
    {
        'id': 1,
        'title': 'Hola desde FastAPI',
        'content': 'Mi primer post con FastAPI'
    },
    {
        'id': 2,
        'title': 'Mi segundo Post con FastAPI',
        'content': 'Mi segundo post con FastAPI blablabla'
    },
    {
        'id': 3,
        'title': 'Django vs FastAPI',
        'content': 'FastAPI es mas rápido por x razones',
        'tags': [
            {
                'name': 'Python'
            },
            {
                'name': 'fastapi'
            },
            {
                'name': 'Django'
            }
        ]
    },
    {
        'id': 4,
        'title': 'Hola desde FastAPI',
        'content': 'Mi primer post con FastAPI'
    },
    {
        'id': 5,
        'title': 'Mi segundo Post con FastAPI',
        'content': 'Mi segundo post con FastAPI blablabla'
    },
    {
        'id': 6,
        'title': 'Django vs FastAPI',
        'content': 'FastAPI es mas rápido por x razones'
    },
    {
        'id': 7,
        'title': 'Hola desde FastAPI',
        'content': 'Mi primer post con FastAPI'
    },
    {
        'id': 8,
        'title': 'Mi segundo Post con FastAPI',
        'content': 'Mi segundo post con FastAPI blablabla'
    },
    {
        'id': 9,
        'title': 'Django vs FastAPI',
        'content': 'FastAPI es mas rápido por x razones'
    },
    {
        'id': 10,
        'title': 'Hola desde FastAPI',
        'content': 'Mi primer post con FastAPI'
    },
    {
        'id': 11,
        'title': 'Mi segundo Post con FastAPI',
        'content': 'Mi segundo post con FastAPI blablabla'
    },
    {
        'id': 12,
        'title': 'Django vs FastAPI',
        'content': 'FastAPI es mas rápido por x razones',
        'tags': [
            {
                'name': 'Python'
            },
            {
                'name': 'fastapi'
            },
            {
                'name': 'Django'
            }
        ]
    },
    {
        'id': 13,
        'title': 'Hola desde FastAPI',
        'content': 'Mi primer post con FastAPI'
    },
    {
        'id': 14,
        'title': 'Mi segundo Post con FastAPI',
        'content': 'Mi segundo post con FastAPI blablabla'
    },
    {
        'id': 15,
        'title': 'Django vs FastAPI',
        'content': 'FastAPI es mas rápido por x razones',
        'tags': [
            {
                'name': 'Python'
            },
            {
                'name': 'fastapi'
            },
            {
                'name': 'Django'
            }
        ]
    }
]


class Tag(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description='Nombre de la etiqueta'
    )


class Author(BaseModel):
    name: str
    email: EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    author: Optional[Author] = None


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
        min_length=2,
        description='Una o mas etiquetas. Ejemplo: ?tags=python&tags=fastapi'
    )
):
    tags_lower = [tag.lower() for tag in tags]

    return [
        post
        for post in BLOG_POST
        if any(
            tag['name'].lower() in tags
            for tag in post.get('tags', [])
        )
    ]


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
    )
):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if not include_content:
                return {'id': post['id'], 'title': post['title']}
            return post

    raise HTTPException(status_code=404, detail='Post no encontrado')


@app.post('/posts', response_model=PostPublic, response_description='Post creado (OK)', status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = PostORM(title=post.title, content=post.content)
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail='Error al crear el post')


@app.put('/posts/{post_id}', response_model=PostPublic, response_description='Post actualizado', response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post['id'] == post_id:
            payload = data.model_dump(
                exclude_unset=True)  # {"title": "Ricardo"}
            if 'title' in payload:
                post['title'] = payload['title']
            if 'content' in payload:
                post['content'] = payload['content']
            return post

    raise HTTPException(status_code=404, detail='Post no encontrado')


@app.delete('/posts/{post_id}', status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post['id'] == post_id:
            BLOG_POST.pop(index)
            return
    raise HTTPException(status_code=404, detail='Post no encontrado')

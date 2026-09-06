from math import ceil
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Union, Literal
from src.core.db import get_db
from .schemas import PostPublic, PaginatedPost, PostCreate, PostUpdate, PostSummary
from .repository import PostRepository

router = APIRouter(prefix='/posts', tags=['posts'])


@router.get('/', response_model=PaginatedPost)
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
    repo = PostRepository(db)
    query = query or text

    total, items = repo.search(
        query,
        order_by,
        direction,
        page,
        per_page
    )

    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)

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

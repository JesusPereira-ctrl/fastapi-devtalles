from fastapi import FastAPI, Query, HTTPException, Path, status, Depends
from typing import Optional, List, Union, Literal
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)  # dev

app = FastAPI(title='Mini Blog')


@app.get('/')
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}


@app.get('/posts/by-tags', response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description='Una o mas etiquetas. Ejemplo: ?tags=python&tags=fastapi'
    ),
    db: Session = Depends(get_db)
):

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
    if not post:
        raise HTTPException(status_code=404, detail='Post no encontrado')

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@app.post('/posts', response_model=PostPublic, response_description='Post creado (OK)', status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = PostORM(
        title=post.title,
        content=post.content,
        author=author_obj
    )

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

    return post


@app.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail='Post no encontrado')

    db.commit()

    return

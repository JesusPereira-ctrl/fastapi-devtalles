from fastapi import FastAPI

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
        'content': 'FastAPI es mas rápido por x razones'
    },
]


@app.get('/')
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}


@app.get('/posts')
def list_posts():
    return {'data': BLOG_POST}

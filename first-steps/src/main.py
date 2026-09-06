from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)  # dev

app = FastAPI(title='Mini Blog')


@app.get('/')
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}

from fastapi import FastAPI
from . import models, books, authors
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book API")

app.include_router(books.router)
app.include_router(authors.router)

@app.get("/")
def root():
    return {"message": "Book API is running"}
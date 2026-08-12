from fastapi import FastAPI
from . import models
from .database import engine
from .routers import books, authors, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book API")

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(authors.router)


@app.get("/")
def root():
    return {"message": "Book API is running"}
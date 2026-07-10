from fastapi import FastAPI
from . import models
from .database import engine
from .routers import books

models .Base.metadata.create_all(bind=engine)
app = FastAPI(title="Book API")
app.include_router(books.router)

@app.get("/")
    def root():
        return{"message": "Book API is running"}
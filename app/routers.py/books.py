from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/books", tags=["books"])


def get_book_or_404(book_id: int, db: Session) -> models.Book:
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/", response_model=List[schemas.BookResponse])
def list_books(db: Session = Depends(get_db)):
    return db.scalars(select(models.Book)).all()


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return get_book_or_404(book_id, db)


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)):
    book = get_book_or_404(book_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = get_book_or_404(book_id, db)
    db.delete(book)
    db.commit()
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from .. import models, schemas
from ..database import get_db
from .dependencies import get_current_user
from .authors import get_author_or_404

router = APIRouter(prefix="/books", tags=["books"])


def get_book_or_404(book_id: int, db: Session, current_user: models.User) -> models.Book:
    book = db.scalar(
        select(models.Book).where(
            models.Book.id == book_id, models.Book.owner_id == current_user.id
        )
    )
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    get_author_or_404(book.author_id, db, current_user)  # no author -> no book, and it must be yours
    db_book = models.Book(**book.model_dump(), owner_id=current_user.id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/", response_model=schemas.PaginatedBooks)
def list_books(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    title: str | None = None,
    author_id: int | None = None,
    published_year: int | None = None,
    sort_by: Literal["id", "title", "published_year"] = "id",
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    base_query = select(models.Book).where(models.Book.owner_id == current_user.id)
    if title:
        base_query = base_query.where(models.Book.title.ilike(f"%{title}%"))
    if author_id is not None:
        base_query = base_query.where(models.Book.author_id == author_id)
    if published_year is not None:
        base_query = base_query.where(models.Book.published_year == published_year)

    total = db.scalar(select(func.count()).select_from(base_query.subquery()))

    sort_column = getattr(models.Book, sort_by)
    items_query = (
        base_query
        .options(selectinload(models.Book.author))
        .order_by(sort_column.desc() if order == "desc" else sort_column.asc())
        .offset(skip)
        .limit(limit)
    )
    items = db.scalars(items_query).all()

    return schemas.PaginatedBooks(total=total, skip=skip, limit=limit, items=items)


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_book_or_404(book_id, db, current_user)


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    payload: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    book = get_book_or_404(book_id, db, current_user)
    update_data = payload.model_dump(exclude_unset=True)
    if "author_id" in update_data:
        get_author_or_404(update_data["author_id"], db, current_user)
    for field, value in update_data.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    book = get_book_or_404(book_id, db, current_user)
    db.delete(book)
    db.commit()
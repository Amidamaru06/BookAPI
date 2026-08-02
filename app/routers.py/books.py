from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..authors import get_author_or_404

router = APIRouter(prefix="/books", tags=["books"])


def get_book_or_404(book_id: int, db: Session):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    get_author_or_404(book.author_id, db)
    
    db_book = models.Book(
        title=book.title,
        description=book.description,
        published_year=book.published_year,
        author_id=book.author_id
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/", response_model=schemas.PaginatedBooks)
def list_books(
    skip: int = 0,
    limit: int = 10,
    title: str = None,
    author_id: int = None,
    published_year: int = None,
    sort_by: str = "id",
    order: str = "asc",
    db: Session = Depends(get_db),
):
    # Start the basic query
    query = db.query(models.Book)
    
    # Apply filters using simple if statements
    if title:
        query = query.filter(models.Book.title.contains(title))
    if author_id is not None:
        query = query.filter(models.Book.author_id == author_id)
    if published_year is not None:
        query = query.filter(models.Book.published_year == published_year)

    total = query.count()

    if sort_by == "title":
        if order == "desc":
            query = query.order_by(models.Book.title.desc())
        else:
            query = query.order_by(models.Book.title.asc())
    elif sort_by == "published_year":
        if order == "desc":
            query = query.order_by(models.Book.published_year.desc())
        else:
            query = query.order_by(models.Book.published_year.asc())
    else:

        if order == "desc":
            query = query.order_by(models.Book.id.desc())
        else:
            query = query.order_by(models.Book.id.asc())


    items = query.offset(skip).limit(limit).all()

    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return get_book_or_404(book_id, db)


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)):
    book = get_book_or_404(book_id, db)
    
    if payload.author_id is not None:
        get_author_or_404(payload.author_id, db)
        book.author_id = payload.author_id
        
    if payload.title is not None:
        book.title = payload.title
    if payload.description is not None:
        book.description = payload.description
    if payload.published_year is not None:
        book.published_year = payload.published_year
        
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = get_book_or_404(book_id, db)
    db.delete(book)
    db.commit()
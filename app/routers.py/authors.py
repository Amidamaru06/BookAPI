from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from  .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/authors", tags=["authors"])


def get_author_or_404(author_id: int, db: Session):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return author


@router.post("/", response_model=schemas.AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    db_author = models.Author(name=author.name, bio=author.bio)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


@router.get("/", response_model=list[schemas.AuthorResponse])
def list_authors(db: Session = Depends(get_db)):
   
    authors = db.query(models.Author).all()
    return authors


@router.get("/{author_id}", response_model=schemas.AuthorResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    return get_author_or_404(author_id, db)


@router.put("/{author_id}", response_model=schemas.AuthorResponse)
def update_author(author_id: int, payload: schemas.AuthorUpdate, db: Session = Depends(get_db)):
    author = get_author_or_404(author_id, db)
    
    if payload.name is not None:
        author.name = payload.name
    if payload.bio is not None:
        author.bio = payload.bio
        
    db.commit()
    db.refresh(author)
    return author


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = get_author_or_404(author_id, db)
    
    if len(author.books) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete an author who still has books assigned",
        )
        
    db.delete(author)
    db.commit()
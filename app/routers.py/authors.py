from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from .. import models, schemas
from ..database import get_db
from ..dependencies import get_current_user
from sqlalchemy.orm import Session
from  .. import models, schemas
from ..database import get_db
router = APIRouter(prefix="/authors", tags=["authors"])


def get_author_or_404(author_id: int, db: Session, current_user: models.User) -> models.Author:
    author = db.scalar(
        select(models.Author).where(
            models.Author.id == author_id, models.Author.owner_id == current_user.id
        )
    )
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return author


@router.post("/", response_model=schemas.AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(
    author: schemas.AuthorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_author = models.Author(**author.model_dump(), owner_id=current_user.id)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


@router.get("/", response_model=list[schemas.AuthorResponse])
def list_authors(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.scalars(
        select(models.Author)
        .where(models.Author.owner_id == current_user.id)
        .options(selectinload(models.Author.books))
    ).all()


@router.get("/{author_id}", response_model=schemas.AuthorResponse)
def get_author(
    author_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_author_or_404(author_id, db, current_user)


@router.put("/{author_id}", response_model=schemas.AuthorResponse)
def update_author(
    author_id: int,
    payload: schemas.AuthorUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    author = get_author_or_404(author_id, db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(author, field, value)
    db.commit()
    db.refresh(author)
    return author


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(
    author_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    author = get_author_or_404(author_id, db, current_user)
    if author.books:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete an author who still has books assigned",
        )
    db.delete(author)
    db.commit()
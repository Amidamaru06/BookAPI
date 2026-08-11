from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]

    books: Mapped[list["Book"]] = relationship(back_populates="owner")
    authors: Mapped[list["Author"]] = relationship(back_populates="owner")


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    bio: Mapped[Optional[str]]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    books: Mapped[list["Book"]] = relationship(back_populates="author")
    owner: Mapped["User"] = relationship(back_populates="authors")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[Optional[str]]
    published_year: Mapped[Optional[int]]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["Author"] = relationship(back_populates="books")
    owner: Mapped["User"] = relationship(back_populates="books")
from pydantic import BaseModel, ConfigDict
class AuthorBrief(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class BookBrief(BaseModel):
    id: int
    title: str
    published_year: int | None = None
    model_config = ConfigDict(from_attributes=True)


#Author

class AuthorBase(BaseModel):
    name: str
    bio: str | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None


class AuthorResponse(AuthorBase):
    id: int
    books: list[BookBrief] = []
    model_config = ConfigDict(from_attributes=True)


#Book

class BookBase(BaseModel):
    title: str
    description: str | None = None
    published_year: int | None = None


class BookCreate(BookBase):
    author_id: int


class BookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    published_year: int | None = None
    author_id: int | None = None


class BookResponse(BookBase):
    id: int
    author: AuthorBrief
    model_config = ConfigDict(from_attributes=True)


#Pagination

class PaginatedBooks(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[BookResponse]
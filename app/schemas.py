from typing import Optional
from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    published_year: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    published_year: Optional[int] = None


class BookResponse(BookBase):
    id: int
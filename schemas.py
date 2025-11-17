from enum import Enum
from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class BookStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"
    reserved = "reserved"


class BookGenre(str, Enum):
    fantasy = "fantasy"
    classic = "classic"
    science = "science"
    history = "history"
    other = "other"


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, example="The Lord of the Rings")
    author: str = Field(..., min_length=1, max_length=50, example="J.R.R. Tolkien")
    year: int = Field(..., ge=1000, le=2100, example=1954)
    isbn: Optional[str] = Field(None, max_length=13, example="9780544003415")
    pages: Optional[int] = Field(None, gt=0, example=500)
    genre: Optional[BookGenre] = Field(default=BookGenre.other)
    status: BookStatus = Field(default=BookStatus.available)

    @field_validator("year")
    @classmethod
    def check_year_not_future(cls, value: int) -> int:
        current_year = date.today().year
        if value > current_year:
            raise ValueError("Год издания не может быть в будущем")
        return value

    @field_validator("isbn")
    @classmethod
    def check_isbn(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.isdigit():
            raise ValueError("ISBN должен содержать только цифры")
        if len(value) not in (10, 13):
            raise ValueError("ISBN должен быть длиной 10 или 13 символов")
        return value


class BookCreate(BookBase):
    """Модель для создания книги"""
    pass


class BookUpdate(BaseModel):
    """Модель для обновления книги (частично)"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    isbn: Optional[str] = Field(None, max_length=13)
    pages: Optional[int] = Field(None, gt=0)
    genre: Optional[BookGenre] = None
    status: Optional[BookStatus] = None
    version: Optional[int] = None

    @field_validator("year")
    @classmethod
    def check_year_not_future(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        current_year = date.today().year
        if value > current_year:
            raise ValueError("Год издания не может быть в будущем")
        return value

    @field_validator("isbn")
    @classmethod
    def check_isbn(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.isdigit():
            raise ValueError("ISBN должен содержать только цифры")
        if len(value) not in (10, 13):
            raise ValueError("ISBN должен быть длиной 10 или 13 символов")
        return value


class Book(BookBase):
    id: int
    created_date: datetime
    version: int = 1


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None

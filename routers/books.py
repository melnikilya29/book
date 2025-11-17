from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query, status

from schemas import Book, BookCreate, BookUpdate, BookStatus
from errors import BookNotFoundError, IsbnAlreadyExistsError, VersionConflictError

router = APIRouter()

book_list: List[Book] = []
book_id_counter: int = 1


def find_book_index_by_id(book_id: int) -> int:
    for index, book in enumerate(book_list):
        if book.id == book_id:
            return index
    raise BookNotFoundError(book_id)


def check_isbn_unique(isbn: Optional[str], ignore_book_id: Optional[int] = None) -> None:
    if isbn is None:
        return
    for book in book_list:
        if book.isbn == isbn and book.id != ignore_book_id:
            raise IsbnAlreadyExistsError(isbn)


@router.get(
    "/",
    response_model=List[Book],
    summary="Получить список книг",
    description="Возвращает список книг с поддержкой пагинации и фильтрации.",
)
async def get_all_books(
    skip: int = Query(0, ge=0, description="Сколько книг пропустить"),
    limit: int = Query(10, gt=0, le=100, description="Сколько книг вернуть"),
    author: Optional[str] = Query(None, description="Фильтр по автору"),
    title: Optional[str] = Query(None, description="Фильтр по части названия"),
    status: Optional[BookStatus] = Query(None, description="Фильтр по статусу"),
    sort_by_year: bool = Query(False, description="Сортировать по году издания"),
):
    books = book_list.copy()

    if author:
        books = [b for b in books if b.author.lower() == author.lower()]

    if title:
        books = [b for b in books if title.lower() in b.title.lower()]

    if status:
        books = [b for b in books if b.status == status]

    if sort_by_year:
        books.sort(key=lambda b: b.year)

    return books[skip: skip + limit]


@router.get(
    "/{book_id}",
    response_model=Book,
    summary="Получить книгу по id",
)
async def get_book_by_id(book_id: int):
    index = find_book_index_by_id(book_id)
    return book_list[index]


@router.post(
    "/",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую книгу",
)
async def create_book(new_book_data: BookCreate):
    global book_id_counter

    check_isbn_unique(new_book_data.isbn)

    new_book = Book(
        id=book_id_counter,
        created_date=datetime.utcnow(),
        version=1,
        **new_book_data.model_dict(),
    )
    book_id_counter += 1
    book_list.append(new_book)
    return new_book


@router.put(
    "/{book_id}",
    response_model=Book,
    summary="Полностью обновить книгу",
)
async def update_book(book_id: int, book_data: BookCreate):
    index = find_book_index_by_id(book_id)

    check_isbn_unique(book_data.isbn, ignore_book_id=book_id)

    old_book = book_list[index]
    updated_book = Book(
        id=old_book.id,
        created_date=old_book.created_date,
        version=old_book.version + 1,
        **book_data.model_dict(),
    )
    book_list[index] = updated_book
    return updated_book


@router.patch(
    "/{book_id}",
    response_model=Book,
    summary="Частично обновить книгу (с версией)",
)
async def patch_book(book_id: int, book_data: BookUpdate):
    index = find_book_index_by_id(book_id)
    current_book = book_list[index]

    if book_data.version is not None and book_data.version != current_book.version:
        raise VersionConflictError(book_id)

    update_data = book_data.model_dict(exclude_unset=True)
    if "isbn" in update_data:
        check_isbn_unique(update_data["isbn"], ignore_book_id=book_id)

    updated_fields = current_book.model_dict()
    updated_fields.update({k: v for k, v in update_data.items() if k != "version"})
    updated_fields["version"] = current_book.version + 1

    updated_book = Book(**updated_fields)
    book_list[index] = updated_book
    return updated_book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить книгу",
)
async def delete_book(book_id: int):
    index = find_book_index_by_id(book_id)
    book_list.pop(index)
    # 204 — без тела
    return




from schemas import Book
from datetime import datetime

book_list = []
book_id_counter = 1


def add_new_book(title: str, author: str, year: int, status: str):
    global book_id_counter
    new_book = Book(
        id=book_id_counter,
        title=title,
        author=author,
        year=year,
        isbn=None,
        pages=None,
        genre="other",
        status=status,
        created_date=datetime.utcnow(),
        version=1
    )
    book_list.append(new_book)
    book_id_counter += 1


def get_book_by_id(book_id: int):
    for book in book_list:
        if book.id == book_id:
            return book
    return None


def update_book(book_id: int, title: str, author: str, year: int, status: str):
    for book in book_list:
        if book.id == book_id:
            book.title = title
            book.author = author
            book.year = year
            book.status = status
            return True
    return False


def delete_book(book_id: int):
    for book in book_list:
        if book.id == book_id:
            book_list.remove(book)
            return True
    return False


from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/books")


@router.get("/")
def get_books(skip: int = 0, limit: int = 10, author: str = None):
    data = book_list

    if author:
        data = [b for b in data if author.lower() in b.author.lower()]

    return data[skip: skip + limit]


@router.get("/{book_id}")
def api_get_book(book_id: int):
    book = get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book


@router.delete("/{book_id}")
def api_delete_book(book_id: int):
    ok = delete_book(book_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return {"status": "deleted"}

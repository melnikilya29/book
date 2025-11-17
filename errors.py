from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from schemas import ErrorResponse


class BookNotFoundError(Exception):
    def __init__(self, book_id: int):
        self.book_id = book_id


class IsbnAlreadyExistsError(Exception):
    def __init__(self, isbn: str):
        self.isbn = isbn


class VersionConflictError(Exception):
    def __init__(self, book_id: int):
        self.book_id = book_id


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BookNotFoundError)
    async def handle_book_not_found(request: Request, exc: BookNotFoundError):
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error="BookNotFound",
                message=f"Книга с id={exc.book_id} не найдена",
                details={"book_id": exc.book_id},
            ).model_dump(),
        )

    @app.exception_handler(IsbnAlreadyExistsError)
    async def handle_isbn_conflict(request: Request, exc: IsbnAlreadyExistsError):
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(
                error="IsbnConflict",
                message="Книга с таким ISBN уже существует",
                details={"isbn": exc.isbn},
            ).model_dump(),
        )

    @app.exception_handler(VersionConflictError)
    async def handle_version_conflict(request: Request, exc: VersionConflictError):
        return JSONResponse(
            status_code=409,
            content=ErrorResponse(
                error="VersionConflict",
                message="Книга была изменена кем-то ещё. Обновите данные и попробуйте снова.",
                details={"book_id": exc.book_id},
            ).model_dump(),
        )

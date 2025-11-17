from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from routers.books_api import (
    book_list,
    add_new_book,
    get_book_by_id,
    update_book,
    delete_book
)

from routers.books_api import router as api_router

app = FastAPI()
app.include_router(api_router)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def show_books(request: Request):
    return templates.TemplateResponse(
        "books_list.html",
        {"request": request, "books": book_list}
    )


@app.get("/add", response_class=HTMLResponse)
async def add_page(request: Request):
    return templates.TemplateResponse(
        "add_book.html",
        {"request": request}
    )


@app.post("/add")
async def add_book_form(
        title: str = Form(...),
        author: str = Form(...),
        year: int = Form(...),
        status: str = Form(...)
):
    add_new_book(title=title, author=author, year=year, status=status)
    return RedirectResponse("/", status_code=302)


@app.get("/edit/{book_id}", response_class=HTMLResponse)
async def edit_page(request: Request, book_id: int):
    book = get_book_by_id(book_id)
    return templates.TemplateResponse(
        "edit_book.html",
        {"request": request, "book": book}
    )


@app.post("/edit/{book_id}")
async def edit_book(
        book_id: int,
        title: str = Form(...),
        author: str = Form(...),
        year: int = Form(...),
        status: str = Form(...)
):
    update_book(book_id, title=title, author=author, year=year, status=status)
    return RedirectResponse("/", status_code=302)


@app.get("/delete/{book_id}")
async def delete_book_ui(book_id: int):
    delete_book(book_id)
    return RedirectResponse("/", status_code=302)

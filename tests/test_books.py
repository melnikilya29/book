from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_book_ok():
    book_data = {
        "title": "Test Book",
        "author": "Tester",
        "year": 2020,
        "isbn": "1234567890",
        "pages": 100,
        "genre": "other",
        "status": "available"
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Test Book"
    assert body["id"] > 0


def test_get_books_list_ok():
    response = client.get("/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_book_not_found():
    response = client.get("/books/99999")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "BookNotFound"

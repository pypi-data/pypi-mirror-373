from typing import List, Dict, Any
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pieql import pieql, QLType

app = FastAPI()


class UsersResponseModel(BaseModel):
    users: List[Dict[str, Any]]


@app.get("/items", response_model=QLType | UsersResponseModel)
@pieql()
def items():
    return JSONResponse({
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Carol"}
        ]
    })


# app = PieQL(app)
client = TestClient(app)


def test_no_schema_returns_full_json():
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert len(data["users"]) == 3


def test_filter_names():
    response = client.get("/items?__schema=users[*].name")
    assert response.status_code == 200
    data = response.json()
    assert data == ["Alice", "Bob", "Carol"]


def test_sum_ids():
    response = client.get("/items?__schema=sum(users[*].id)")
    assert response.status_code == 200
    data = response.json()
    assert data == 6


def test_filter_by_id():
    response = client.get("/items?__schema=users[?id==`2`]")
    assert response.status_code == 200
    data = response.json()
    assert data == [{"id": 2, "name": "Bob"}]


def test_invalid_jmespath_returns_400():
    response = client.get("/items?__schema=users[??].name")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

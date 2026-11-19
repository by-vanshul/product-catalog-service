from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.models.product import Product


# Keep app import-time database initialization isolated from PostgreSQL.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

with patch("sqlalchemy.create_engine", return_value=test_engine):
    from app.main import app

from app.database.dependencies import get_db

Base.metadata.create_all(bind=test_engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    session.query(Product).delete()
    session.commit()

    try:
        yield session
    finally:
        session.rollback()
        session.query(Product).delete()
        session.commit()
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def create_sample_product(client: TestClient) -> dict:
    response = client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "category": "Accessories",
            "price": 29.99,
            "quantity": 10,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_products_for_listing(client: TestClient) -> list[dict]:
    products = []
    for name, price in (
        ("Alpha", 40),
        ("Bravo", 10),
        ("Charlie", 30),
        ("Delta", 20),
    ):
        response = client.post(
            "/products",
            json={
                "name": name,
                "category": "Electronics",
                "price": price,
                "quantity": 1,
            },
        )
        assert response.status_code == 201
        products.append(response.json())
    return products


def test_health(client):
    # The health endpoint responds successfully.
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_create_product(client):
    # Creating a valid product returns 201 and includes its ID and timestamp.
    response = client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "category": "Accessories",
            "price": 29.99,
            "quantity": 10,
        },
    )

    assert response.status_code == 201
    product = response.json()
    assert product["id"]
    assert product["created_at"]
    assert product["name"] == "Wireless Mouse"
    assert product["category"] == "Accessories"
    assert product["price"] == 29.99
    assert product["quantity"] == 10


def test_get_products(client):
    # Listing products returns successfully and includes a previously created product.
    created_product = create_sample_product(client)

    response = client.get("/products")

    assert response.status_code == 200
    products = response.json()
    assert any(product["id"] == created_product["id"] for product in products)


def test_get_products_filters_by_name_case_insensitively(client):
    matching_product = create_sample_product(client)
    client.post(
        "/products",
        json={
            "name": "Mechanical Keyboard",
            "category": "Accessories",
            "price": 59.99,
            "quantity": 5,
        },
    )

    response = client.get("/products", params={"name": "MOUSE"})

    assert response.status_code == 200
    assert [product["id"] for product in response.json()] == [
        matching_product["id"]
    ]


def test_get_products_filters_by_category_case_insensitively(client):
    matching_product = create_sample_product(client)
    client.post(
        "/products",
        json={
            "name": "Desk Lamp",
            "category": "Lighting",
            "price": 39.99,
            "quantity": 3,
        },
    )

    response = client.get("/products", params={"category": "ACCESS"})

    assert response.status_code == 200
    assert [product["id"] for product in response.json()] == [
        matching_product["id"]
    ]


def test_get_products_combines_name_and_category_filters(client):
    matching_product = create_sample_product(client)
    client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "category": "Office",
            "price": 24.99,
            "quantity": 4,
        },
    )

    response = client.get(
        "/products",
        params={"name": "wireless", "category": "access"},
    )

    assert response.status_code == 200
    assert [product["id"] for product in response.json()] == [
        matching_product["id"]
    ]


def test_get_products_paginates_results(client):
    products = create_products_for_listing(client)

    first_page = client.get(
        "/products",
        params={"page": 1, "size": 2},
    )
    second_page = client.get(
        "/products",
        params={"page": 2, "size": 2},
    )

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    ordered_ids = sorted(product["id"] for product in products)
    assert [product["id"] for product in first_page.json()] == ordered_ids[:2]
    assert [product["id"] for product in second_page.json()] == ordered_ids[2:]


@pytest.mark.parametrize(
    ("sort_by", "order", "expected_names"),
    [
        ("name", "asc", ["Alpha", "Bravo", "Charlie", "Delta"]),
        ("name", "desc", ["Delta", "Charlie", "Bravo", "Alpha"]),
        ("price", "asc", ["Bravo", "Delta", "Charlie", "Alpha"]),
        ("price", "desc", ["Alpha", "Charlie", "Delta", "Bravo"]),
    ],
)
def test_get_products_sorts_results(client, sort_by, order, expected_names):
    create_products_for_listing(client)

    response = client.get(
        "/products",
        params={"sort_by": sort_by, "order": order},
    )

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == expected_names


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"size": 0},
        {"sort_by": "category"},
        {"order": "ascending"},
    ],
)
def test_get_products_rejects_invalid_pagination_and_sort_params(client, params):
    response = client.get("/products", params=params)

    assert response.status_code == 422


def test_get_products_combines_filters_pagination_and_sorting(client):
    client.post(
        "/products",
        json={
            "name": "iPhone 15",
            "category": "Mobile",
            "price": 800,
            "quantity": 2,
        },
    )
    client.post(
        "/products",
        json={
            "name": "iPhone 16",
            "category": "Mobile",
            "price": 900,
            "quantity": 2,
        },
    )
    client.post(
        "/products",
        json={
            "name": "iPhone case",
            "category": "Accessories",
            "price": 20,
            "quantity": 5,
        },
    )

    response = client.get(
        "/products",
        params={
            "name": "iphone",
            "category": "mobile",
            "page": 1,
            "size": 1,
            "sort_by": "price",
            "order": "desc",
        },
    )

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == ["iPhone 16"]


def test_get_product_by_id(client):
    # Fetching an existing product by ID returns its details.
    created_product = create_sample_product(client)

    response = client.get(f"/products/{created_product['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created_product["id"]
    assert response.json()["created_at"]


def test_update_product(client):
    # Updating an existing product returns 200 with the changed values.
    created_product = create_sample_product(client)

    response = client.put(
        f"/products/{created_product['id']}",
        json={"price": 34.99, "quantity": 7},
    )

    assert response.status_code == 200
    updated_product = response.json()
    assert updated_product["id"] == created_product["id"]
    assert updated_product["price"] == 34.99
    assert updated_product["quantity"] == 7


def test_delete_product(client):
    # Deleting an existing product returns 200 and removes it from subsequent lookup.
    created_product = create_sample_product(client)

    response = client.delete(f"/products/{created_product['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created_product["id"]
    assert response.json()["created_at"]
    assert client.get(f"/products/{created_product['id']}").status_code == 404


def test_get_nonexistent_product_returns_404(client):
    # Looking up an unknown product ID returns 404.
    response = client.get("/products/not-a-product")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_nonexistent_product_returns_404(client):
    # Updating an unknown product ID returns 404.
    response = client.put(
        "/products/not-a-product",
        json={"price": 12.5},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_nonexistent_product_returns_404(client):
    # Deleting an unknown product ID returns 404.
    response = client.delete("/products/not-a-product")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_create_product_negative_price_returns_422(client):
    # A negative price fails request validation.
    response = client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "category": "Accessories",
            "price": -1,
            "quantity": 10,
        },
    )

    assert response.status_code == 422


def test_create_product_negative_quantity_returns_422(client):
    # A negative quantity fails request validation.
    response = client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "category": "Accessories",
            "price": 29.99,
            "quantity": -1,
        },
    )

    assert response.status_code == 422


def test_create_product_missing_name_returns_422(client):
    # Omitting the required name fails request validation.
    response = client.post(
        "/products",
        json={
            "category": "Accessories",
            "price": 29.99,
            "quantity": 10,
        },
    )

    assert response.status_code == 422


def test_create_product_missing_category_returns_422(client):
    # Omitting the required category fails request validation.
    response = client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "price": 29.99,
            "quantity": 10,
        },
    )

    assert response.status_code == 422


def test_create_product_empty_name_returns_422(client):
    # An empty name fails the minimum-length validation.
    response = client.post(
        "/products",
        json={
            "name": "",
            "category": "Accessories",
            "price": 29.99,
            "quantity": 10,
        },
    )

    assert response.status_code == 422


def test_create_product_empty_category_returns_422(client):
    # An empty category fails the minimum-length validation.
    response = client.post(
        "/products",
        json={
            "name": "Wireless Mouse",
            "category": "",
            "price": 29.99,
            "quantity": 10,
        },
    )

    assert response.status_code == 422

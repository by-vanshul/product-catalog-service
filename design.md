# Product Catalog Service

## Overview

A lightweight Product Catalog Microservice built using FastAPI.

The service provides CRUD APIs for managing products and follows a layered architecture to ensure maintainability, testability, and scalability.

---

## High Level Design

```text
Client
   |
   v
FastAPI (API Layer)
   |
   v
Service Layer
   |
   v
SQLAlchemy (ORM)
   |
   v
PostgreSQL
```

---

## Project Structure

```text
app/
├── api/          # REST API endpoints
├── services/     # Business logic
├── models/       # Database models
├── schemas/      # Request/Response schemas
├── database/     # Database configuration
└── main.py       # Application entry point
```

---

## Product Data Model

| Field | Type |
|---------|---------|
| id | UUID |
| name | String |
| category | String |
| price | Float |
| quantity | Integer |
| created_at | Timestamp |

---

## API Endpoints

### Create Product

```http
POST /products
```

### Get All Products

```http
GET /products
```

### Get Product By ID

```http
GET /products/{id}
```

### Update Product

```http
PUT /products/{id}
```

### Delete Product

```http
DELETE /products/{id}
```

---

## Validation Rules

- name is required
- category is required
- price must be greater than or equal to 0
- quantity must be greater than or equal to 0

---

## Error Handling

| Status Code | Description |
|-------------|-------------|
| 400/422 | Validation Error |
| 404 | Product Not Found |
| 500 | Internal Server Error |


---

### Design Decision

- Product updates support both full and partial updates. Clients may send the complete product payload or only the fields that need to be modified.
- API responses may be standardized using a message + data structure.

---

## Future Enhancements

- Search Products
- Pagination
- Sorting
- JWT Authentication
- Docker Support
- GitHub Actions CI/CD
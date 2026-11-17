# Product Catalog Service

## HLD

Client
-> FastAPI
-> Service Layer
-> SQLAlchemy
-> PostgreSQL

## Product Model

id,
name,
category,
price,
quantity,
created_at

## APIs

POST /products

GET /products
GET /products/{id}

PUT /products/{id}

DELETE /products/{id}
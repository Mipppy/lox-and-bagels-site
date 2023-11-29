DROP TABLE IF EXISTS products;
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL,
    price TEXT NOT NULL,
    outofstock BOOLEAN NOT NULL
)
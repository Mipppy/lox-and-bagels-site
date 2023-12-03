-- DROP TABLE IF EXISTS products;
-- CREATE TABLE products (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     description TEXT NOT NULL,
--     type TEXT NOT NULL,
--     price INTEGER NOT NULL,
--     outofstock BOOLEAN NOT NULL,
--     image TEXT NOT NULL,
--     shortname TEXT NOT NULL
-- );
-- DROP TABLE IF EXISTS cart;
-- CREATE TABLE cart (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     product TEXT NOT NULL,
--     quanity INTEGER NOT NULL,
--     modifiers TEXT NOT NULL,
--     price INTEGER NOT NULL,
--     user INTEGER REFERENCES users(id)
-- );
-- DELETE FROM products WHERE name = 'Everything Bagel';
-- INSERT INTO products (name, description,type,price,outofstock,image,shortname) VALUES ('Onion Bagel', 'eeww yucky bagel','bagel',150,0,'https://www.newyorkerbagels.com/cdn/shop/files/onion-bagels-single-198_480x480.jpg?v=1696048368', 'onion_bagel')
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL
)
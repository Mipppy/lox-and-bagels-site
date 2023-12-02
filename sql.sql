-- DROP TABLE IF EXISTS products;
-- CREATE TABLE products (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     description TEXT NOT NULL,
--     type TEXT NOT NULL,
--     price TEXT NOT NULL,
--     outofstock BOOLEAN NOT NULL,
--     image TEXT NOT NULL,
--     shortname TEXT NOT NULL
-- );
-- INSERT INTO products (name, description, type, price, outofstock, image, shortname) VALUES ('show', 'This is a test product! Made by tim :)', 'test', '$50000', 1, 'https://img.freepik.com/free-psd/3d-rendering-chocolate-donut_250435-1211.jpg?w=1800&t=st=1701394389~exp=1701394989~hmac=8915b2b2f430f720e351b69910adb77ef984527adafdfdfe09db6ca74efd3961','test5');
DROP TABLE IF EXISTS cart;
CREATE TABLE cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT NOT NULL,
    quanity INTEGER NOT NULL,
    modifiers TEXT NOT NULL,
    price TEXT NOT NULL,
    user INTEGER REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tracking (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    url TEXT,
    seuil NUMERIC,
    user_id INT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS scrap (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES tracking(id),
    price NUMERIC,
    scrap_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

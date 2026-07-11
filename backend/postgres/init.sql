CREATE TABLE users (
    uuid VARCHAR(50) PRIMARY KEY,
    password VARCHAR(128),
    img VARCHAR(128)
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(50) REFERENCES users(uuid),
    accuracy int,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    length int
);

CREATE TABLE passages (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    length INT NOT NULL,
    language VARCHAR(10) DEFAULT 'en'
);

CREATE INDEX idx_passages_length ON passages(length);
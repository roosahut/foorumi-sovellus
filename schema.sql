CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role INTEGER
);

CREATE TABLE forums (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    name TEXT
);

CREATE TABLE chains (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    forum_id INTEGER REFERENCES forums,
    headline TEXT
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    writer_id INTEGER REFERENCES users,
    chain_id INTEGER REFERENCES chains,
    message TEXT
    sent_at TIMESTAMPTZ DEFAULT Now()
);
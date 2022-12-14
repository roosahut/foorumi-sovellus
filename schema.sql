CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role INTEGER
);

CREATE TABLE forums (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    name TEXT,
    deleted BOOLEAN,
    is_secret BOOLEAN
);

CREATE TABLE chains (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES users,
    forum_id INTEGER REFERENCES forums,
    headline TEXT,
    deleted BOOLEAN
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    writer_id INTEGER REFERENCES users,
    chain_id INTEGER REFERENCES chains,
    message TEXT,
    sent_at TIMESTAMPTZ DEFAULT Now(),
    deleted BOOLEAN
);

CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    liker_id INTEGER REFERENCES users,
    message_id INTEGER REFERENCES messages,
    is_unlike BOOLEAN
);

CREATE TABLE has_access (
    id SERIAL PRIMARY KEY,
    forum_id INTEGER REFERENCES forums,
    user_id INTEGER REFERENCES users
);
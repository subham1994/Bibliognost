DROP TABLE IF EXISTS users;

DROP EXTENSION IF EXISTS CITEXT CASCADE;
CREATE EXTENSION CITEXT;

CREATE TABLE users (
    id UUID UNIQUE,
    name TEXT NOT NULL,
    email CITEXT PRIMARY KEY,
    role TEXT NOT NULL,
    avatarhash TEXT,
    bio TEXT,
    location TEXT,
    password TEXT NOT NULL,
    createtime BIGINT NOT NULL,
    updatetime BIGINT NOT NULL,
    lastscene BIGINT NOT NULL
);
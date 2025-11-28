CREATE TABLE IF NOT EXISTS colonies (
    id UUID PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    colony_name TEXT NOT NULL,
    theme_color TEXT,
    banner_file TEXT,
    database_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- Colony Schema Initialization
-- Tables that belong to EACH colony database
-- ============================================================

-- ============= ITEMS TABLE =============
CREATE TABLE IF NOT EXISTS colony_items (
    id SERIAL PRIMARY KEY,

    -- Basic item info
    name TEXT NOT NULL,
    description TEXT,

    -- Points
    points_per_item INTEGER NOT NULL CHECK (points_per_item > 0),

    -- Media
    image_path TEXT,
    thumbnail_path TEXT,

    -- External references
    website_url TEXT,

    -- Organization
    category TEXT,
    tags TEXT[],

    -- Restriction rules
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    max_allowed INTEGER CHECK (max_allowed >= 0),
    default_quantity INTEGER NOT NULL DEFAULT 1 CHECK (default_quantity > 0),

    -- Audit timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_colony_items_name ON colony_items (name);
CREATE INDEX IF NOT EXISTS idx_colony_items_category ON colony_items (category);


-- ============= OPTIONAL FUTURE TABLES =============

-- Items selected per user (shopping history)
CREATE TABLE IF NOT EXISTS colony_item_selections (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES colony_items(id) ON DELETE CASCADE,
    username TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_item_selections_user ON colony_item_selections(username);
CREATE INDEX IF NOT EXISTS idx_item_selections_item ON colony_item_selections(item_id);

-- Logging actions (admin, edits, etc.)
CREATE TABLE IF NOT EXISTS colony_logs (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

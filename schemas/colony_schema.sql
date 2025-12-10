-- ============= ITEMS TABLE =============
CREATE TABLE IF NOT EXISTS colony_items (
    id SERIAL PRIMARY KEY,

    -- Basic item info
    name TEXT NOT NULL,
    description TEXT,

    -- Points
    points_per_item INTEGER NOT NULL CHECK (points_per_item > 0),

    -- Media
    thumbnail_path TEXT,

    -- External references
    website_url TEXT,

    -- Organization
    category TEXT,
    tags TEXT[],

    -- Vendor (NEW)
    vendor TEXT,

    -- Item code as text (NEW)
    item_number TEXT,
    model_number TEXT,

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
CREATE INDEX IF NOT EXISTS idx_colony_items_vendor ON colony_items (vendor);
CREATE INDEX IF NOT EXISTS idx_colony_items_item_number ON colony_items (item_number);
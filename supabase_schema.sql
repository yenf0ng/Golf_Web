-- ============================================================
--  Golf Swing Tracker — Supabase SQL DDL
--  Run these in your Supabase SQL Editor
-- ============================================================

-- 1. VIDEO VAULT TABLE
-- Stores metadata for every uploaded swing clip.
CREATE TABLE IF NOT EXISTS video_vault (
    id            BIGSERIAL PRIMARY KEY,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    clip_date     DATE        NOT NULL,
    category      TEXT        NOT NULL CHECK (category IN ('Putting', 'Driver', 'Irons', 'Woods')),
    notes         TEXT,
    storage_path  TEXT        NOT NULL,   -- Supabase Storage object path
    public_url    TEXT        NOT NULL    -- Full public URL for playback
);

-- Index for fast filtering by category
CREATE INDEX IF NOT EXISTS idx_video_vault_category ON video_vault(category);
CREATE INDEX IF NOT EXISTS idx_video_vault_clip_date ON video_vault(clip_date DESC);

-- 2. PERFORMANCE LOGS TABLE
-- Stores per-shot practice session data.
CREATE TABLE IF NOT EXISTS performance_logs (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_date    DATE        NOT NULL,
    club_used       TEXT        NOT NULL CHECK (club_used IN (
                        'Driver','3-Wood','5-Wood','Hybrid',
                        '3-Iron','4-Iron','5-Iron','6-Iron',
                        '7-Iron','8-Iron','9-Iron',
                        'PW','GW','SW','LW','Putter'
                    )),
    total_distance  INTEGER     NOT NULL CHECK (total_distance >= 0),
    carry_distance  INTEGER     NOT NULL CHECK (carry_distance >= 0),
    shot_shape      TEXT        NOT NULL CHECK (shot_shape IN (
                        'Straight','Draw','Fade',
                        'Push','Pull','Slice','Hook'
                    )),
    notes           TEXT
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_perf_logs_session_date  ON performance_logs(session_date DESC);
CREATE INDEX IF NOT EXISTS idx_perf_logs_club_used     ON performance_logs(club_used);
CREATE INDEX IF NOT EXISTS idx_perf_logs_shot_shape    ON performance_logs(shot_shape);

-- ============================================================
--  Supabase Storage Bucket
--  Create manually in the Supabase dashboard OR via API:
--
--  Bucket name  : swing-clips
--  Public       : true   (so public_url links work without auth)
-- ============================================================

-- ============================================================
--  RLS FIX: Run this in Supabase SQL Editor
--  Fixes the 403 "new row violates row-level security policy"
--  error on INSERT for video_vault and performance_logs.
-- ============================================================

-- OPTION A (Recommended for personal apps): Disable RLS entirely.
-- Since this is a personal app behind an admin password in Streamlit,
-- you don't need Postgres-level RLS.

ALTER TABLE video_vault       DISABLE ROW LEVEL SECURITY;
ALTER TABLE performance_logs  DISABLE ROW LEVEL SECURITY;


-- ============================================================
--  OPTION B: Keep RLS enabled but allow the anon key to
--  INSERT/SELECT/UPDATE/DELETE. Use this if you want RLS on
--  but still need the app to work with the anon key.
--  (Run INSTEAD of Option A if you prefer this approach.)
-- ============================================================

-- -- video_vault policies
-- CREATE POLICY "anon can select" ON video_vault
--   FOR SELECT USING (true);
--
-- CREATE POLICY "anon can insert" ON video_vault
--   FOR INSERT WITH CHECK (true);
--
-- CREATE POLICY "anon can delete" ON video_vault
--   FOR DELETE USING (true);
--
-- -- performance_logs policies
-- CREATE POLICY "anon can select" ON performance_logs
--   FOR SELECT USING (true);
--
-- CREATE POLICY "anon can insert" ON performance_logs
--   FOR INSERT WITH CHECK (true);
--
-- CREATE POLICY "anon can delete" ON performance_logs
--   FOR DELETE USING (true);


-- ============================================================
--  STORAGE BUCKET POLICY FIX
--  If uploads also return 403, add this in:
--  Supabase Dashboard -> Storage -> swing-clips -> Policies
--  OR run the SQL below.
-- ============================================================

-- Allow public read (needed for public_url to work)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('swing-clips', 'swing-clips', true)
-- ON CONFLICT (id) DO UPDATE SET public = true;

-- Allow anon to upload & delete objects
CREATE POLICY "anon upload"  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'swing-clips');

CREATE POLICY "anon read"    ON storage.objects FOR SELECT
  USING (bucket_id = 'swing-clips');

CREATE POLICY "anon delete"  ON storage.objects FOR DELETE
  USING (bucket_id = 'swing-clips');

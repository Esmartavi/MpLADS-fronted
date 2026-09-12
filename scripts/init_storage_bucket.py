"""
BHARAT-DRISHTI // Initialize Supabase Storage Bucket & Test Connection
======================================================================
Creates the 'raw-mplads-archives' bucket in Supabase Storage.
"""

import os
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.db_helper import get_db_connection
conn = get_db_connection()
conn.autocommit = True
cur = conn.cursor()

print("[*] Creating 'raw-mplads-archives' bucket in Supabase Storage...")
cur.execute("""
    INSERT INTO storage.buckets (id, name, public)
    VALUES ('raw-mplads-archives', 'raw-mplads-archives', true)
    ON CONFLICT (id) DO NOTHING;
""")

cur.execute("SELECT id, name, public, created_at FROM storage.buckets;")
buckets = cur.fetchall()
print("[OK] Supabase Storage Buckets:")
for b in buckets:
    print(f"   * Bucket ID: {b[0]} | Name: {b[1]} | Public: {b[2]} | Created: {b[3]}")

conn.close()

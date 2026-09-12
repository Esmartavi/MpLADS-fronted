import os
import psycopg2
import re
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
print("Original DATABASE_URL:", db_url)

# Connect helper that supports pooler fallback
def connect_db(url):
    try:
        return psycopg2.connect(url, connect_timeout=5)
    except Exception as e:
        print(f"Direct connection failed: {e}")
        # Try pooler fallback
        m = re.match(r"postgresql://([^:]+):([^@]+)@db\.([a-z0-9]+)\.supabase\.co:(\d+)/(.+)", url)
        if m:
            user, pwd, ref, port, db = m.groups()
            pooler_url = f"postgresql://postgres.{ref}:{pwd}@aws-0-ap-south-1.pooler.supabase.com:5432/{db}"
            print(f"Trying pooler: postgresql://postgres.{ref}:***@aws-0-ap-south-1.pooler.supabase.com:5432/{db}")
            return psycopg2.connect(pooler_url, connect_timeout=8)
        raise

conn = connect_db(db_url)
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
tables = [r[0] for r in cur.fetchall()]
print(f"Found {len(tables)} tables:")
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}";')
    cnt = cur.fetchone()[0]
    print(f"  * {t}: {cnt:,} rows")

cur.close()
conn.close()
print("Done!")

"""
BHARAT-DRISHTI // Resilient Supabase PostgreSQL Connection Helper
==================================================================
Handles direct connections and automatically falls back to the official
Supabase connection pooler (port 5432 session mode) when direct DNS host 
translation is unavailable on IPv4 networks.
"""

import os
import re
import psycopg2
from dotenv import load_dotenv

# Ensure .env is loaded
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, ".env"))


def get_db_connection(db_url: str = None, connect_timeout: int = 6):
    """
    Connect to PostgreSQL with automatic pooler fallback.
    Supports both direct host and Supabase AWS-0 pooler routing.
    """
    raw_url = db_url or os.getenv("DATABASE_URL")
    if not raw_url:
        return None

    # Try primary connection
    try:
        conn = psycopg2.connect(raw_url.strip(), connect_timeout=connect_timeout)
        conn.autocommit = True
        return conn
    except Exception as primary_err:
        err_msg = str(primary_err)
        # If host lookup fails on db.<ref>.supabase.co, route through the Supabase connection pooler
        if "could not translate host name" in err_msg or "Name or service not known" in err_msg or "11001" in err_msg:
            # Check for DATABASE_POOLER_URL
            pooler_env = os.getenv("DATABASE_POOLER_URL")
            if pooler_env:
                try:
                    conn = psycopg2.connect(pooler_env.strip(), connect_timeout=connect_timeout)
                    conn.autocommit = True
                    return conn
                except Exception:
                    pass

            # Parse direct Supabase URL: postgresql://[user]:[pwd]@db.[ref].supabase.co:[port]/[db]
            m = re.match(r"^postgresql://([^:]+):([^@]+)@db\.([a-z0-9]+)\.supabase\.co(?::\d+)?/(.+)$", raw_url.strip())
            if m:
                _user, pwd, ref, db_name = m.groups()
                # Region ap-south-1 (Mumbai) as per MoSPI deployment architecture
                pooler_host = "aws-0-ap-south-1.pooler.supabase.com"
                pooler_user = f"postgres.{ref}"
                pooler_url = f"postgresql://{pooler_user}:{pwd}@{pooler_host}:5432/{db_name}"
                try:
                    conn = psycopg2.connect(pooler_url, connect_timeout=connect_timeout)
                    conn.autocommit = True
                    return conn
                except Exception as pooler_err:
                    print(f"[!] Supabase pooler connection fallback error: {pooler_err}")
                    raise pooler_err from primary_err
        raise primary_err

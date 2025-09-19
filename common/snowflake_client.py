import snowflake.connector
from contextlib import contextmanager

# シークレット辞書（st.secrets.get("snowflake")）を受け取って接続を返す
def _connect(sf):
    return snowflake.connector.connect(
        user=sf["user"],
        password=sf["password"],
        account=sf["account"],
        warehouse=sf.get("warehouse"),
        database=sf.get("database"),
        schema=sf.get("schema"),
        role=sf.get("role")
    )

@contextmanager
def snowflake_connection(sf):
    """
    コンテキストマネージャーで接続を扱う:
    with snowflake_connection(sf) as conn:
        cur = conn.cursor()
        ...
    """
    if not sf:
        raise ValueError("Snowflake のシークレットが提供されていません")
    conn = None
    try:
        conn = _connect(sf)
        yield conn
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

def fetch_single_value(sf, query):
    """
    単一値を取得するユーティリティ（簡易版）
    """
    with snowflake_connection(sf) as conn:
        cur = conn.cursor()
        try:
            cur.execute(query)
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()
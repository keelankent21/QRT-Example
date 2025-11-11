import json, sqlite3, pandas as pd

DB_PATH = "qrt_history.db"

def _connect():
    return sqlite3.connect(DB_PATH)

def save_analysis(params: dict, res: dict):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS analyses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts DATETIME DEFAULT CURRENT_TIMESTAMP,
        params TEXT,
        exec_summary TEXT,
        risks_csv TEXT
    )""")
    risks_csv = ""
    if "risks" in res and hasattr(res["risks"], "to_csv"):
        risks_csv = res["risks"].to_csv(index=False)
    cur.execute("INSERT INTO analyses(params, exec_summary, risks_csv) VALUES (?,?,?)",
                (json.dumps(params), res.get("executive_summary",""), risks_csv))
    conn.commit(); conn.close()

def list_analyses(limit=50):
    conn = _connect()
    df = pd.read_sql_query("SELECT id, ts FROM analyses ORDER BY id DESC LIMIT ?", conn, params=(limit,))
    conn.close(); return df

def load_analysis(analysis_id: int):
    conn = _connect()
    row = pd.read_sql_query("SELECT * FROM analyses WHERE id=?", conn, params=(analysis_id,)).iloc[0]
    conn.close()
    return row

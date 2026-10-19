import sqlite3
from datetime import datetime


class AuditLog:
    def __init__(self, path="audit.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_log("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "ts TEXT, txn_id TEXT, step TEXT, detail TEXT)"
        )

    def log(self, txn_id, step, detail):
        self.conn.execute(
            "INSERT INTO audit_log (ts, txn_id, step, detail) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), txn_id, step, detail),
        )
        self.conn.commit()

    def rows(self):
        cur = self.conn.execute("SELECT ts, txn_id, step, detail FROM audit_log ORDER BY id")
        return cur.fetchall()


if __name__ == "__main__":
    audit = AuditLog()
    audit.log("T006", "FLAGGED", "duplicate payment")
    audit.log("T006", "APPROVED", "human decision")
    for row in audit.rows():
        print(row)
        
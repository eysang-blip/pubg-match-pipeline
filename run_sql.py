import sqlite3
import sys

# SQL 파일 하나를 실행하고 결과를 표처럼 출력한다
# 사용법: python run_sql.py verify/01_bot_ratio.sql

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    query = f.read()

conn = sqlite3.connect("pubg.db")
cur = conn.execute(query)
columns = [c[0] for c in cur.description]

print(" | ".join(columns))
for row in cur.fetchall():
    print(" | ".join(str(v) for v in row))

conn.close()

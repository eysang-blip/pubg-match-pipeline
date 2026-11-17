import json
import glob
import sqlite3
from collections import Counter

conn = sqlite3.connect("pubg.db")
cur = conn.cursor()

# 1) DB에 매치별로 몇 명이 들어갔는지
db_counts = dict(
    cur.execute("SELECT match_id, COUNT(*) FROM participants GROUP BY match_id")
)

# 2) 원본 JSON의 참가자 수와 비교
raw_total = 0
mismatch = 0
modes = Counter()

for path in glob.glob("data/*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    match_id = data["data"]["id"]
    modes[data["data"]["attributes"]["gameMode"]] += 1

    raw = sum(1 for i in data["included"] if i["type"] == "participant")
    raw_total += raw
    saved = db_counts.get(match_id, 0)

    if raw != saved:
        mismatch += 1
        print(f"불일치: {match_id[:8]}... 원본 {raw}명 / DB {saved}명")

print("원본 참가자 합계:", raw_total, "/ DB 행 수:", sum(db_counts.values()))
print("불일치 매치 수:", mismatch)
print("게임 모드별 매치 수:", dict(modes))

# 3) 매치당 참가자 수 분포
print(
    "매치당 참가자 수 (최소, 최대, 평균):",
    cur.execute(
        "SELECT MIN(c), MAX(c), AVG(c) FROM "
        "(SELECT COUNT(*) AS c FROM participants GROUP BY match_id)"
    ).fetchone(),
)

conn.close()
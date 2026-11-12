import csv
import glob
import os
import sqlite3

# sql/ 폴더의 쿼리를 번호 순서대로 실행하고 결과를 출력한다.
# 마지막 검토 후보 목록(06)은 output/review_candidates.csv로도 저장한다.

conn = sqlite3.connect("pubg.db")
cur = conn.cursor()
os.makedirs("output", exist_ok=True)

for path in sorted(glob.glob("sql/*.sql")):
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        query = f.read()

    # 01은 뷰를 만드는 쿼리라 결과가 없다
    if name.startswith("01"):
        cur.executescript(query)
        print(f"[{name}] 정제 뷰 생성 완료\n")
        continue

    cur.execute(query)
    columns = [c[0] for c in cur.description]
    rows = cur.fetchall()

    print(f"[{name}] {len(rows)}행")
    print("  " + " | ".join(columns))
    for row in rows[:15]:
        print("  " + " | ".join(str(v) for v in row))
    print()

    if name.startswith("06"):
        with open("output/review_candidates.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        print(f"검토 후보 {len(rows)}건을 output/review_candidates.csv에 저장\n")

conn.close()

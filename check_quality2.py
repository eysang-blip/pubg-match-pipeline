import json
import glob
from collections import defaultdict

# 1) 매치별 정보 모으기
rows = []
for path in glob.glob("data/*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    attrs = data["data"]["attributes"]
    p = sum(1 for i in data["included"] if i["type"] == "participant")
    r = sum(1 for i in data["included"] if i["type"] == "roster")
    rows.append(
        (data["data"]["id"][:8], attrs["gameMode"], attrs["mapName"],
         attrs["duration"], p, r)
    )

# 2) 참가자가 50명 미만인 매치 출력
print("참가자 50명 미만 매치 (id, 모드, 맵, 시간(초), 참가자, roster):")
for row in sorted(rows, key=lambda x: x[4]):
    if row[4] < 50:
        print(row)

# 3) 모드별 요약
print()
summary = defaultdict(list)
for _, mode, _, _, p, r in rows:
    summary[mode].append((p, r))

for mode, vals in summary.items():
    ps = [v[0] for v in vals]
    rs = [v[1] for v in vals]
    print(f"{mode}: 매치 {len(vals)}개 / 참가자 {min(ps)}~{max(ps)}명 / roster {min(rs)}~{max(rs)}개")
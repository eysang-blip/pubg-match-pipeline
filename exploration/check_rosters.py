import json
import glob
from collections import Counter, defaultdict

# 모드별로 "roster 하나에 몇 명이 들어 있는지" 분포 세기
sizes = defaultdict(Counter)

for path in glob.glob("data/*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    mode = data["data"]["attributes"]["gameMode"]
    if data["data"]["attributes"]["mapName"] == "Range_Main":
        continue  # 연습장 매치는 제외

    for item in data["included"]:
        if item["type"] == "roster":
            n = len(item["relationships"]["participants"]["data"])
            sizes[mode][n] += 1

for mode, counter in sizes.items():
    print(f"{mode}: roster 인원수별 개수 {dict(sorted(counter.items()))}")
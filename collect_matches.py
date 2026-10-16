import os
import json
import time
import requests
from dotenv import load_dotenv

# 1) 설정
load_dotenv()
API_KEY = os.getenv("PUBG_API_KEY")
PLATFORM = "steam"
LIMIT = 50  # 이번에 받을 매치 개수

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json",
}

# 2) 매치 ID 목록 읽기
with open("match_ids.txt") as f:
    match_ids = f.read().splitlines()[:LIMIT]

os.makedirs("data", exist_ok=True)
saved, skipped, failed = 0, 0, 0

# 3) 하나씩 받아서 저장
for i, match_id in enumerate(match_ids, start=1):
    path = f"data/{match_id}.json"

    # 이미 받은 매치는 건너뜀
    if os.path.exists(path):
        skipped += 1
        continue

    url = f"https://api.pubg.com/shards/{PLATFORM}/matches/{match_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False)
        saved += 1
    else:
        failed += 1
        print(f"[{i}] 실패 {response.status_code}: {match_id}")

    time.sleep(0.5)  # 서버에 부담 주지 않게 잠깐 쉬기

# 4) 결과 요약
print(f"저장 {saved}개 / 건너뜀 {skipped}개 / 실패 {failed}개")
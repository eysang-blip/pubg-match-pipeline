import os
import json
import requests
from dotenv import load_dotenv

# 1) 키 읽기
load_dotenv()
API_KEY = os.getenv("PUBG_API_KEY")
PLATFORM = "steam"

# 2) match_ids.txt에서 첫 번째 매치 ID 읽기
with open("match_ids.txt") as f:
    match_ids = f.read().splitlines()
match_id = match_ids[0]

# 3) 매치 상세 요청
url = f"https://api.pubg.com/shards/{PLATFORM}/matches/{match_id}"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json",
}
response = requests.get(url, headers=headers)
print("상태 코드:", response.status_code)

if response.status_code == 200:
    data = response.json()

    # 4) 원본을 파일로 저장 (나중에 구조를 보려고)
    os.makedirs("data", exist_ok=True)
    with open(f"data/{match_id}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 5) 구조 요약 출력
    attrs = data["data"]["attributes"]
    print("게임 모드:", attrs.get("gameMode"))
    print("맵:", attrs.get("mapName"))
    print("진행 시간(초):", attrs.get("duration"))

    counts = {}
    for item in data["included"]:
        counts[item["type"]] = counts.get(item["type"], 0) + 1
    print("included 종류별 개수:", counts)

    participants = [i for i in data["included"] if i["type"] == "participant"]
    print("참가자 stats 항목:", list(participants[0]["attributes"]["stats"].keys()))
else:
    print("실패:", response.text)
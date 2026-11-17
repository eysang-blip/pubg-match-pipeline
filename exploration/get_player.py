import os
import requests
from dotenv import load_dotenv

# 1) .env 파일에서 API 키 읽기
load_dotenv()
API_KEY = os.getenv("PUBG_API_KEY")

# 2) 조회할 플레이어와 플랫폼 (여기만 바꾸면 됨)
PLATFORM = "steam"          # steam 또는 kakao
PLAYER_NAME = "your_nickname"

# 3) 요청 주소와 헤더 만들기
url = f"https://api.pubg.com/shards/{PLATFORM}/players"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json",
}
params = {"filter[playerNames]": PLAYER_NAME}

# 4) API 호출
response = requests.get(url, headers=headers, params=params)
print("상태 코드:", response.status_code)

# 5) 결과 처리
if response.status_code == 200:
    player = response.json()["data"][0]
    match_ids = [m["id"] for m in player["relationships"]["matches"]["data"]]
    print("플레이어 ID:", player["id"])
    print("가져온 매치 수:", len(match_ids))
    print("매치 ID 앞 3개:", match_ids[:3])
else:
    print("실패:", response.text)
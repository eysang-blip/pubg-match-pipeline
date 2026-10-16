import os
import requests
from dotenv import load_dotenv

# 1) 키 읽기
load_dotenv()
API_KEY = os.getenv("PUBG_API_KEY")

# 2) 샘플 매치 목록 요청
PLATFORM = "steam"
url = f"https://api.pubg.com/shards/{PLATFORM}/samples"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json",
}
response = requests.get(url, headers=headers)
print("상태 코드:", response.status_code)

# 3) 결과 처리
if response.status_code == 200:
    data = response.json()["data"]
    match_ids = [m["id"] for m in data["relationships"]["matches"]["data"]]
    print("받은 매치 수:", len(match_ids))
    print("매치 ID 앞 3개:", match_ids[:3])

    # 4) 나중에 쓰려고 파일에 저장
    with open("match_ids.txt", "w") as f:
        f.write("\n".join(match_ids))
    print("match_ids.txt 저장 완료")
else:
    print("실패:", response.text)
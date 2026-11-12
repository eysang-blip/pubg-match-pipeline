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
response = requests.get(url, headers=headers, timeout=30)
print("상태 코드:", response.status_code)

# 3) 결과 처리
if response.status_code == 200:
    data = response.json()["data"]
    new_ids = [m["id"] for m in data["relationships"]["matches"]["data"]]
    print("받은 매치 수:", len(new_ids))

    # 4) 기존 목록에 새 ID만 추가 (덮어쓰지 않음)
    #    매일 실행하면 목록이 누적되고, 수집 단계에서 이미 받은 것은 건너뛴다
    old_ids = []
    if os.path.exists("match_ids.txt"):
        with open("match_ids.txt") as f:
            old_ids = f.read().splitlines()
    known = set(old_ids)
    added = [m for m in new_ids if m not in known]

    # 새 ID를 앞에 둔다: /samples ID는 시간이 지나면 만료되므로 최신 것부터 받기 위해
    with open("match_ids.txt", "w") as f:
        f.write("\n".join(added + old_ids))
    print(f"새 ID {len(added)}개 추가, 전체 {len(added) + len(old_ids)}개")
else:
    print("실패:", response.text)

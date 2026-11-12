import os
import json
import time
import requests
from dotenv import load_dotenv

# 1) 설정
load_dotenv()
API_KEY = os.getenv("PUBG_API_KEY")
PLATFORM = "steam"
LIMIT = None         # 받을 매치 개수 상한 (None이면 목록 전체)
MAX_RETRY = 3        # 429(요청 너무 많음)일 때 재시도 횟수
EXPIRED_FILE = "expired_ids.txt"   # 404로 확인된 만료 ID 기록 (다음 실행 때 다시 요청하지 않음)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json",
}

# 2) 매치 ID 목록과 이미 만료로 확인된 ID 읽기
with open("match_ids.txt") as f:
    match_ids = f.read().splitlines()[:LIMIT]

expired = set()
if os.path.exists(EXPIRED_FILE):
    with open(EXPIRED_FILE) as f:
        expired = set(f.read().splitlines())

os.makedirs("data", exist_ok=True)
saved, skipped, expired_now, failed = 0, 0, 0, 0


def fetch(match_id):
    """매치 하나를 요청한다. 429면 기다렸다가 재시도, 네트워크 오류도 재시도."""
    url = f"https://api.pubg.com/shards/{PLATFORM}/matches/{match_id}"
    for attempt in range(1, MAX_RETRY + 1):
        try:
            response = requests.get(url, headers=headers, timeout=30)
        except requests.RequestException as e:
            print(f"  네트워크 오류 ({attempt}/{MAX_RETRY}): {e}")
            time.sleep(5 * attempt)
            continue

        if response.status_code != 429:
            return response

        # 서버가 기다릴 시간을 알려주면 그만큼, 아니면 60초 대기
        wait = int(response.headers.get("Retry-After", 60))
        print(f"  429 호출 제한 ({attempt}/{MAX_RETRY}), {wait}초 대기")
        time.sleep(wait)
    return None


# 3) 하나씩 받아서 저장
for i, match_id in enumerate(match_ids, start=1):
    path = f"data/{match_id}.json"

    # 이미 받은 매치, 이미 만료로 확인된 매치는 건너뜀 (증분 수집)
    if os.path.exists(path) or match_id in expired:
        skipped += 1
        continue

    response = fetch(match_id)

    if response is not None and response.status_code == 200:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False)
        saved += 1
    elif response is not None and response.status_code == 404:
        # 오래된 매치는 PUBG 서버에서 삭제되어 404가 난다
        expired_now += 1
        with open(EXPIRED_FILE, "a") as f:
            f.write(match_id + "\n")
    else:
        failed += 1
        code = response.status_code if response is not None else "재시도 초과"
        print(f"[{i}] 실패 {code}: {match_id}")

    time.sleep(0.5)  # 서버에 부담 주지 않게 잠깐 쉬기

# 4) 결과 요약
print(f"저장 {saved}개 / 건너뜀 {skipped}개 / 만료(404) {expired_now}개 / 실패 {failed}개")

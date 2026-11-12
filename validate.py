import glob
import json
import os
import sqlite3
import sys
from datetime import datetime

# 데이터 품질 자동 점검
# - 기존 check_*.py에서 눈으로 확인하던 항목을 "통과/실패"로 판정한다
# - 결과는 화면과 logs/validation_날짜.log에 남기고, 실패가 있으면 종료 코드 1을 돌려준다
#   (파이프라인이 실패한 데이터로 분석까지 넘어가지 않게 하기 위해)

# 참가자가 0~1명이어도 정상인 매치 종류 (원본 JSON으로 확인함)
#   trainingroom: 훈련장. duration 0, 참가자 데이터 자체가 없음
#   tutorialatoz: 튜토리얼. 혼자 플레이
NON_GAME_TYPES = ("trainingroom", "tutorialatoz")


def count_raw_participants(data_dir="data"):
    """원본 JSON의 매치별 참가자 수"""
    counts = {}
    for path in glob.glob(f"{data_dir}/*.json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        counts[data["data"]["id"]] = sum(
            1 for i in data["included"] if i["type"] == "participant"
        )
    return counts


def run_checks(conn, raw_counts):
    """점검 항목을 실행하고 (이름, 통과 여부, 상세) 목록을 돌려준다"""
    cur = conn.cursor()
    one = lambda q: cur.execute(q).fetchone()[0]
    results = []

    # 1) 원본과 DB 대조: 매치 수, 매치별 참가자 수
    db_counts = dict(cur.execute(
        "SELECT match_id, COUNT(*) FROM participants GROUP BY match_id"
    ))
    db_matches = one("SELECT COUNT(*) FROM matches")
    results.append(("원본 매치 수 = DB 매치 수",
                     db_matches == len(raw_counts),
                     f"원본 {len(raw_counts)} / DB {db_matches}"))

    mismatch = [m for m, n in raw_counts.items() if db_counts.get(m, 0) != n]
    results.append(("매치별 참가자 수 원본과 일치",
                     len(mismatch) == 0,
                     f"불일치 {len(mismatch)}건"))

    # 2) 중복: 같은 매치에 같은 플레이어가 두 번 들어갔는지
    dup = one("SELECT COUNT(*) FROM (SELECT 1 FROM participants "
              "GROUP BY match_id, player_id HAVING COUNT(*) > 1)")
    results.append(("(매치, 플레이어) 중복 없음", dup == 0, f"{dup}건"))

    # 3) 참가자 0~1명 매치는 훈련장·튜토리얼이어야 함
    placeholders = ",".join("?" * len(NON_GAME_TYPES))
    odd = cur.execute(f"""
        SELECT COUNT(*) FROM matches m
        WHERE (SELECT COUNT(*) FROM participants p WHERE p.match_id = m.match_id) <= 1
          AND (m.match_type IS NULL OR m.match_type NOT IN ({placeholders}))
    """, NON_GAME_TYPES).fetchone()[0]
    results.append(("참가자 0~1명 매치는 모두 훈련장/튜토리얼", odd == 0,
                    f"원인 불명 {odd}건"))

    # 4) 값 검사: NULL, 음수, 논리 오류
    nulls = one("SELECT COUNT(*) FROM participants WHERE kills IS NULL "
                "OR damage_dealt IS NULL OR time_survived IS NULL OR win_place IS NULL")
    results.append(("주요 컬럼 NULL 없음", nulls == 0, f"{nulls}건"))

    neg = one("SELECT COUNT(*) FROM participants WHERE kills < 0 OR damage_dealt < 0 "
              "OR time_survived < 0 OR walk_distance < 0 OR ride_distance < 0")
    results.append(("음수 값 없음", neg == 0, f"{neg}건"))

    hs = one("SELECT COUNT(*) FROM participants WHERE headshot_kills > kills")
    results.append(("헤드샷 킬 <= 킬", hs == 0, f"위반 {hs}건"))

    over = one("SELECT COUNT(*) FROM participants p JOIN matches m "
               "ON p.match_id = m.match_id WHERE p.time_survived > m.duration + 10 "
               "AND m.match_type NOT IN ('trainingroom', 'tutorialatoz')")
    results.append(("생존 시간 <= 매치 시간 + 10초", over == 0, f"위반 {over}건"))

    # 5) 봇 표시가 player_id 규칙과 맞는지
    bot_bad = one("SELECT COUNT(*) FROM participants WHERE "
                  "(is_bot = 1) != (player_id LIKE 'ai.%')")
    results.append(("is_bot = player_id 'ai.' 여부", bot_bad == 0, f"불일치 {bot_bad}건"))

    return results


def main():
    conn = sqlite3.connect("pubg.db")
    results = run_checks(conn, count_raw_participants())
    conn.close()

    os.makedirs("logs", exist_ok=True)
    now = datetime.now()
    lines = [f"[{now:%Y-%m-%d %H:%M:%S}] 데이터 품질 점검"]
    for name, ok, detail in results:
        lines.append(f"  {'통과' if ok else '실패'} | {name} | {detail}")
    failed = sum(1 for _, ok, _ in results if not ok)
    lines.append(f"  결과: {len(results)}개 중 {len(results) - failed}개 통과")

    text = "\n".join(lines)
    print(text)
    with open(f"logs/validation_{now:%Y%m%d}.log", "a", encoding="utf-8") as f:
        f.write(text + "\n")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

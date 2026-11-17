import sqlite3

conn = sqlite3.connect("pubg.db")
cur = conn.cursor()

# 연습장 맵은 제외하고 보기 위한 공통 조건
BASE = """
FROM participants p
JOIN matches m ON p.match_id = m.match_id
WHERE m.map_name != 'Range_Main'
"""

def run(title, query):
    result = cur.execute(query).fetchall()
    print(f"[{title}]")
    for row in result:
        print("  ", row)
    print()

# 1) 분석 대상 규모
run("분석 대상 (매치 수, 참가자 수)",
    "SELECT COUNT(DISTINCT p.match_id), COUNT(*) " + BASE)

# 2) 누락값(NULL) 개수
run("NULL 개수 (kills, damage_dealt, time_survived, win_place)",
    "SELECT SUM(p.kills IS NULL), SUM(p.damage_dealt IS NULL), "
    "SUM(p.time_survived IS NULL), SUM(p.win_place IS NULL) " + BASE)

# 3) 음수 값
run("음수 값이 있는 행",
    "SELECT COUNT(*) " + BASE +
    " AND (p.kills < 0 OR p.damage_dealt < 0 OR p.time_survived < 0 "
    "OR p.walk_distance < 0 OR p.ride_distance < 0)")

# 4) 헤드샷 킬이 전체 킬보다 많은 경우 (논리 오류)
run("헤드샷 킬 > 킬인 행",
    "SELECT COUNT(*) " + BASE + " AND p.headshot_kills > p.kills")

# 5) 생존 시간이 매치 진행 시간보다 긴 경우 (여유 10초)
run("생존 시간 > 매치 시간 + 10초인 행",
    "SELECT COUNT(*) " + BASE + " AND p.time_survived > m.duration + 10")

# 6) 순위 범위
run("순위 범위 (win_place 최소, 최대)",
    "SELECT MIN(p.win_place), MAX(p.win_place) " + BASE)

conn.close()
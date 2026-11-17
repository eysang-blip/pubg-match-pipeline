import sqlite3
import statistics

MODE = "squad"  # 분석할 게임 모드

conn = sqlite3.connect("pubg.db")
cur = conn.cursor()

# 1) 연습장 제외 + 한 모드만 가져오기
rows = cur.execute(
    """
    SELECT p.kills, p.damage_dealt, p.headshot_kills, p.time_survived
    FROM participants p
    JOIN matches m ON p.match_id = m.match_id
    WHERE m.map_name != 'Range_Main' AND m.game_mode = ?
    """,
    (MODE,),
).fetchall()
print(f"모드 {MODE}: 참가자 {len(rows)}명")

# 2) 피해량 분포와 이상치 기준선 계산
damages = [r[1] for r in rows]
q1, q2, q3 = statistics.quantiles(damages, n=4)
fence = q3 + 3 * (q3 - q1)
print(f"피해량 Q1={q1:.0f}, 중앙값={q2:.0f}, Q3={q3:.0f}, 기준선={fence:.0f}")

# 3) 기준선을 넘은 플레이어
flagged = [r for r in rows if r[1] > fence]
print(f"기준선 초과: {len(flagged)}명 ({len(flagged) / len(rows) * 100:.1f}%)")

print("초과자 상위 10명:")
for kills, dmg, hs, surv in sorted(flagged, key=lambda r: -r[1])[:10]:
    print(f"  킬 {kills}, 피해량 {dmg:.0f}, 헤드샷킬 {hs}, 생존 {surv / 60:.1f}분")

# 4) 헤드샷 비율 비교 (킬 5 이상인 사람만)
def headshot_rate(group):
    g = [r for r in group if r[0] >= 5]
    total_kills = sum(r[0] for r in g)
    if total_kills == 0:
        return "해당자 없음"
    return f"{sum(r[2] for r in g) / total_kills:.2f} (대상 {len(g)}명)"

print("헤드샷 비율 - 전체:", headshot_rate(rows))
print("헤드샷 비율 - 초과자:", headshot_rate(flagged))

conn.close()
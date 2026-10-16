import sqlite3
import statistics

MODE = "squad"

conn = sqlite3.connect("pubg.db")
cur = conn.cursor()

rows = cur.execute(
    """
    SELECT p.kills, p.damage_dealt, p.headshot_kills,
           p.time_survived, p.win_place
    FROM participants p
    JOIN matches m ON p.match_id = m.match_id
    WHERE m.map_name != 'Range_Main' AND m.game_mode = ?
    """,
    (MODE,),
).fetchall()

# 1) 기준선 계산 (이전과 같은 방식)
damages = [r[1] for r in rows]
q1, _, q3 = statistics.quantiles(damages, n=4)
fence = q3 + 3 * (q3 - q1)

flagged = [r for r in rows if r[1] > fence]
normal = [r for r in rows if r[1] <= fence]

# 2) 초과자 vs 나머지: 순위와 생존 시간 (순위는 숫자가 작을수록 좋음)
for name, g in [("초과자", flagged), ("나머지", normal)]:
    place = statistics.median(r[4] for r in g)
    surv = statistics.median(r[3] for r in g) / 60
    print(f"{name} {len(g)}명: 순위 중앙값 {place}, 생존 중앙값 {surv:.1f}분")

# 3) 헤드샷 비율: 킬 3 이상인 사람만, 초과자 vs 나머지를 따로
def hs_rate(group):
    g = [r for r in group if r[0] >= 3]
    kills = sum(r[0] for r in g)
    if kills == 0:
        return "해당자 없음"
    return f"{sum(r[2] for r in g) / kills:.2f} (대상 {len(g)}명)"

print("헤드샷 비율 - 초과자:", hs_rate(flagged))
print("헤드샷 비율 - 나머지:", hs_rate(normal))

# 4) 분당 피해량 상위 5명 (5분 이상 생존한 사람만)
timed = [r for r in rows if r[3] >= 300]
timed.sort(key=lambda r: -(r[1] / (r[3] / 60)))
print("분당 피해량 상위 5명:")
for kills, dmg, hs, surv, place in timed[:5]:
    print(f"  분당 피해량 {dmg / (surv / 60):.0f}, 킬 {kills}, 생존 {surv / 60:.1f}분, 순위 {place}")

conn.close()
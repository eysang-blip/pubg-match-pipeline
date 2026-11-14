-- 매치 안에서 비교한 분당 피해량 z-score
-- 매치마다 로비 수준이 달라서, 전체 기준이 아니라 "같은 매치 사람들 대비" 얼마나 벗어났는지 본다
-- z = (내 분당 피해량 - 매치 평균) / 매치 표준편차
-- SQLite에는 표준편차 함수가 없어서 sqrt(제곱의 평균 - 평균의 제곱)으로 계산한다
-- 주의: 교전이 거의 없던 매치는 표준편차가 작아서 z가 크게 튄다 (분당 피해량 6.0인데 z 5.57이 나온 행이 그 예).
--       그래서 06번 검토 후보에서는 전체 상위 10% 하한을 함께 건다
WITH base AS (
    SELECT match_id, player_id, kills, headshot_kills, damage_dealt,
           time_survived, win_place,
           damage_dealt / (time_survived / 60.0) AS dpm      -- 분당 피해량
    FROM clean_squad
    WHERE time_survived >= 300                              -- 5분 미만 생존자는 분모가 작아 수치가 튐
),
match_stats AS (
    SELECT *,
           AVG(dpm) OVER w AS match_avg,
           SQRT(AVG(dpm * dpm) OVER w - AVG(dpm) OVER w * AVG(dpm) OVER w) AS match_sd,
           COUNT(*) OVER w AS match_n
    FROM base
    WINDOW w AS (PARTITION BY match_id)
)
SELECT match_id, player_id, kills, ROUND(damage_dealt) AS damage,
       ROUND(time_survived / 60.0, 1) AS survival_min, win_place,
       ROUND(dpm, 1) AS dpm, ROUND(match_avg, 1) AS match_avg,
       ROUND((dpm - match_avg) / match_sd, 2) AS z
FROM match_stats
WHERE match_n >= 20        -- 비교할 사람이 20명 미만인 매치는 평균이 불안정해서 제외
  AND match_sd > 0
ORDER BY z DESC
LIMIT 10;

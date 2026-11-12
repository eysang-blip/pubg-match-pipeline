-- 플레이어 기록실: 2판 이상 나온 플레이어의 누적 전적
-- /samples는 무작위 매치라 같은 사람이 여러 번 나오는 경우가 적다 (최대 3판)
SELECT
    player_id,
    COUNT(*)                                AS games,
    SUM(kills)                              AS total_kills,
    ROUND(AVG(damage_dealt), 1)             AS avg_damage,
    ROUND(AVG(time_survived) / 60.0, 1)     AS avg_survival_min,
    MIN(win_place)                          AS best_place,
    SUM(CASE WHEN win_place = 1 THEN 1 ELSE 0 END) AS wins
FROM clean_squad
GROUP BY player_id
HAVING COUNT(*) >= 2
ORDER BY avg_damage DESC
LIMIT 10;

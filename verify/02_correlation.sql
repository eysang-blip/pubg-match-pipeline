WITH t AS (
    SELECT
        p.damage_dealt / (p.time_survived / 60.0) AS x,
        p.kills AS y
    FROM participants p
    JOIN matches m ON p.match_id = m.match_id
    WHERE m.game_mode = 'squad'
      AND m.match_type IN ('official', 'competitive')
      AND p.player_id NOT LIKE 'ai.%'
      AND p.time_survived >= 300
)
SELECT
    COUNT(*) AS n,
    ROUND(
        (AVG(x * y) - AVG(x) * AVG(y))
        / (SQRT(AVG(x * x) - AVG(x) * AVG(x)) * SQRT(AVG(y * y) - AVG(y) * AVG(y))),
    2) AS corr
FROM t;

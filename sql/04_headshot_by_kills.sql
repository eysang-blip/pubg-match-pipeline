-- 킬 수 구간별 헤드샷 비율: 표본(킬 수)이 작을수록 비율이 극단값(0% 또는 100%)으로 튄다
-- -> 비율 지표에 "킬 5 이상" 같은 최소 표본 조건이 필요한 근거
SELECT
    CASE
        WHEN kills = 1 THEN '1킬'
        WHEN kills = 2 THEN '2킬'
        WHEN kills BETWEEN 3 AND 4 THEN '3~4킬'
        WHEN kills BETWEEN 5 AND 9 THEN '5~9킬'
        ELSE '10킬 이상'
    END AS kill_group,
    COUNT(*) AS players,
    ROUND(AVG(headshot_kills * 1.0 / kills), 2) AS avg_hs_ratio,
    ROUND(AVG(CASE WHEN headshot_kills = kills THEN 1.0 ELSE 0 END) * 100, 1) AS pct_hs_100
FROM clean_squad
WHERE kills >= 1
GROUP BY kill_group
ORDER BY MIN(kills);

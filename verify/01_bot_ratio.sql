SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN player_id LIKE 'ai.%' THEN 1 ELSE 0 END) AS bots,
    ROUND(SUM(CASE WHEN player_id LIKE 'ai.%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS bot_pct
FROM participants;

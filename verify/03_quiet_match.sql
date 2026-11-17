SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN player_id LIKE 'ai.%' THEN 1 ELSE 0 END) AS bots,
    SUM(CASE WHEN player_id NOT LIKE 'ai.%' THEN 1 ELSE 0 END) AS humans,
    SUM(CASE WHEN player_id NOT LIKE 'ai.%' THEN kills ELSE 0 END) AS human_kills,
    ROUND(AVG(CASE WHEN player_id NOT LIKE 'ai.%' THEN damage_dealt END), 1) AS human_avg_damage
FROM participants
WHERE match_id LIKE '2872ba49%';

-- 정제 단계별로 몇 명이 남는지 (데이터가 어디서 얼마나 빠지는지 확인)
SELECT '1. 전체 참가자' AS step, COUNT(*) AS rows
FROM participants
UNION ALL
SELECT '2. squad 모드만', COUNT(*)
FROM participants p JOIN matches m ON p.match_id = m.match_id
WHERE m.game_mode = 'squad'
UNION ALL
SELECT '3. 정규 매치만 (봇전 제외)', COUNT(*)
FROM participants p JOIN matches m ON p.match_id = m.match_id
WHERE m.game_mode = 'squad' AND m.match_type IN ('official', 'competitive')
UNION ALL
SELECT '4. 사람만 (봇 제외)', COUNT(*)
FROM clean_squad;

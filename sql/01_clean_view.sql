-- 분석용 정제 데이터 (임시 뷰)
-- 조건: squad 모드 / 정규 매치(official=일반, competitive=랭크) / 사람만(봇 제외)
-- 빠지는 것: 훈련장·튜토리얼(참가자 0~1명 매치), 봇전(airoyale), 봇 참가자
CREATE TEMP VIEW IF NOT EXISTS clean_squad AS
SELECT p.*, m.match_type, m.duration
FROM participants p
JOIN matches m ON p.match_id = m.match_id
WHERE m.game_mode = 'squad'
  AND m.match_type IN ('official', 'competitive')
  AND p.is_bot = 0;

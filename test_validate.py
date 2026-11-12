import sqlite3
import unittest

from validate import run_checks

# 점검 로직이 일부러 넣은 오류를 실제로 잡아내는지 확인하는 테스트
# 실행: python -m unittest test_validate.py


def make_db():
    """테스트용 작은 DB (메모리에만 만들어짐)"""
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE matches (match_id TEXT PRIMARY KEY, game_mode TEXT,
            match_type TEXT, map_name TEXT, duration INTEGER, created_at TEXT);
        CREATE TABLE participants (match_id TEXT, player_id TEXT, is_bot INTEGER,
            kills INTEGER, assists INTEGER, dbnos INTEGER, headshot_kills INTEGER,
            damage_dealt REAL, time_survived REAL, walk_distance REAL,
            ride_distance REAL, win_place INTEGER, kill_place INTEGER);
        INSERT INTO matches VALUES ('m1', 'squad', 'official', 'Baltic_Main', 1800, '');
    """)
    add(conn, "m1", "account.a", kills=3, hs=1)
    add(conn, "m1", "ai.1", kills=0, hs=0)
    return conn


def add(conn, match_id, player_id, kills=1, hs=0, dmg=100.0, surv=600.0):
    is_bot = 1 if player_id.startswith("ai.") else 0
    conn.execute(
        "INSERT INTO participants VALUES (?,?,?,?,0,0,?,?,?,100,0,1,1)",
        (match_id, player_id, is_bot, kills, hs, dmg, surv),
    )


def failed_checks(conn, raw_counts):
    return [name for name, ok, _ in run_checks(conn, raw_counts) if not ok]


class TestValidate(unittest.TestCase):
    def test_clean_data_passes(self):
        conn = make_db()
        self.assertEqual(failed_checks(conn, {"m1": 2}), [])

    def test_missing_rows_detected(self):
        # 원본에는 3명인데 DB에는 2명 -> 적재 누락
        conn = make_db()
        self.assertIn("매치별 참가자 수 원본과 일치", failed_checks(conn, {"m1": 3}))

    def test_duplicate_detected(self):
        conn = make_db()
        add(conn, "m1", "account.a")
        self.assertIn("(매치, 플레이어) 중복 없음", failed_checks(conn, {"m1": 3}))

    def test_headshot_more_than_kills_detected(self):
        conn = make_db()
        add(conn, "m1", "account.b", kills=1, hs=2)
        self.assertIn("헤드샷 킬 <= 킬", failed_checks(conn, {"m1": 3}))

    def test_survival_longer_than_match_detected(self):
        conn = make_db()
        add(conn, "m1", "account.b", surv=5000)
        self.assertIn("생존 시간 <= 매치 시간 + 10초", failed_checks(conn, {"m1": 3}))

    def test_empty_training_room_is_ok(self):
        # 훈련장 매치는 참가자 0명이어도 정상
        conn = make_db()
        conn.execute("INSERT INTO matches VALUES ('t1','clansolo','trainingroom','Range_Main',0,'')")
        self.assertEqual(failed_checks(conn, {"m1": 2, "t1": 0}), [])

    def test_empty_official_match_detected(self):
        # 일반 매치인데 참가자가 0명이면 원인 불명으로 실패해야 함
        conn = make_db()
        conn.execute("INSERT INTO matches VALUES ('m2','squad','official','Baltic_Main',1800,'')")
        self.assertIn("참가자 0~1명 매치는 모두 훈련장/튜토리얼",
                      failed_checks(conn, {"m1": 2, "m2": 0}))


if __name__ == "__main__":
    unittest.main()

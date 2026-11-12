import json
import sqlite3
import glob

# DB는 data/ 폴더의 원본 JSON으로 언제든 다시 만들 수 있는 "파생 데이터"다.
# 그래서 매번 테이블을 지우고 처음부터 다시 만든다.
# (컬럼을 추가해도 기존 행이 옛날 구조로 남는 문제가 없고, 몇 번을 돌려도 결과가 같다)

# 1) DB 파일 열기 (없으면 새로 만들어짐)
conn = sqlite3.connect("pubg.db")
cur = conn.cursor()

# 2) 테이블 새로 만들기
cur.execute("DROP TABLE IF EXISTS participants")
cur.execute("DROP TABLE IF EXISTS matches")

cur.execute("""
CREATE TABLE matches (
    match_id   TEXT PRIMARY KEY,
    game_mode  TEXT,
    match_type TEXT,     -- official(일반), competitive(랭크), airoyale(봇전), trainingroom(훈련장), tutorialatoz(튜토리얼)
    map_name   TEXT,
    duration   INTEGER,
    created_at TEXT
)
""")

cur.execute("""
CREATE TABLE participants (
    match_id       TEXT,
    player_id      TEXT,     -- 'account.'로 시작하면 사람, 'ai.'로 시작하면 봇
    is_bot         INTEGER,  -- 1이면 봇
    kills          INTEGER,
    assists        INTEGER,
    dbnos          INTEGER,
    headshot_kills INTEGER,
    damage_dealt   REAL,
    time_survived  REAL,
    walk_distance  REAL,
    ride_distance  REAL,
    win_place      INTEGER,
    kill_place     INTEGER,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id) REFERENCES matches (match_id)
)
""")

# 3) data 폴더의 JSON 파일을 읽어서 저장
for path in glob.glob("data/*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    match_id = data["data"]["id"]
    attrs = data["data"]["attributes"]

    cur.execute(
        """INSERT OR IGNORE INTO matches
           (match_id, game_mode, match_type, map_name, duration, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (match_id, attrs.get("gameMode"), attrs.get("matchType"),
         attrs.get("mapName"), attrs.get("duration"), attrs.get("createdAt")),
    )

    for item in data["included"]:
        if item["type"] != "participant":
            continue
        s = item["attributes"]["stats"]
        is_bot = 1 if s["playerId"].startswith("ai.") else 0
        cur.execute(
            """INSERT OR IGNORE INTO participants
               (match_id, player_id, is_bot, kills, assists, dbnos, headshot_kills,
                damage_dealt, time_survived, walk_distance, ride_distance,
                win_place, kill_place)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (match_id, s["playerId"], is_bot, s["kills"], s["assists"], s["DBNOs"],
             s["headshotKills"], s["damageDealt"], s["timeSurvived"],
             s["walkDistance"], s["rideDistance"], s["winPlace"], s["killPlace"]),
        )

conn.commit()

# 4) 잘 들어갔는지 확인
print("matches 행 수:", cur.execute("SELECT COUNT(*) FROM matches").fetchone()[0])
print("participants 행 수:", cur.execute("SELECT COUNT(*) FROM participants").fetchone()[0])
print("봇 행 수:", cur.execute("SELECT SUM(is_bot) FROM participants").fetchone()[0])

conn.close()

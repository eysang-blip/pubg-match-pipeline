import json
import sqlite3
import glob

# 1) DB 파일 열기 (없으면 새로 만들어짐)
conn = sqlite3.connect("pubg.db")
cur = conn.cursor()

# 2) 테이블 만들기
cur.execute("""
CREATE TABLE IF NOT EXISTS matches (
    match_id   TEXT PRIMARY KEY,
    game_mode  TEXT,
    map_name   TEXT,
    duration   INTEGER,
    created_at TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS participants (
    match_id       TEXT,
    player_id      TEXT,
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
           (match_id, game_mode, map_name, duration, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (match_id, attrs.get("gameMode"), attrs.get("mapName"),
         attrs.get("duration"), attrs.get("createdAt")),
    )

    for item in data["included"]:
        if item["type"] != "participant":
            continue
        s = item["attributes"]["stats"]
        cur.execute(
            """INSERT OR IGNORE INTO participants
               (match_id, player_id, kills, assists, dbnos, headshot_kills,
                damage_dealt, time_survived, walk_distance, ride_distance,
                win_place, kill_place)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (match_id, s["playerId"], s["kills"], s["assists"], s["DBNOs"],
             s["headshotKills"], s["damageDealt"], s["timeSurvived"],
             s["walkDistance"], s["rideDistance"], s["winPlace"], s["killPlace"]),
        )

conn.commit()

# 4) 잘 들어갔는지 확인
print("matches 행 수:", cur.execute("SELECT COUNT(*) FROM matches").fetchone()[0])
print("participants 행 수:", cur.execute("SELECT COUNT(*) FROM participants").fetchone()[0])
print("피해량 상위 3명 (킬, 피해량):")
for row in cur.execute(
    "SELECT kills, damage_dealt FROM participants ORDER BY damage_dealt DESC LIMIT 3"
):
    print(row)

conn.close()
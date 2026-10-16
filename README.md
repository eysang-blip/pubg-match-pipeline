# PUBG Match Pipeline

PUBG 공식 API로 매치 데이터를 수집해 SQLite DB로 정리하고, 데이터 품질을 점검한 뒤 플레이어 기록의 이상치를 분석하는 프로젝트입니다.

수집 → 저장 → 검증 → 분석의 각 단계를 별도 스크립트로 나눠, 단계마다 결과를 확인하고 다음 단계로 넘어가는 방식으로 진행했습니다.

## 파이프라인 구성

| 단계 | 스크립트 | 하는 일 |
|---|---|---|
| 1. 매치 목록 수집 | `get_samples.py` | `/samples` 엔드포인트에서 매치 ID 735개를 받아 `match_ids.txt`에 저장 |
| 2. 구조 확인 | `get_match.py` | 매치 1개의 원본 JSON을 받아 응답 구조와 참가자 stats 항목 확인 |
| 3. 매치 상세 수집 | `collect_matches.py` | 매치 50개를 `data/`에 JSON으로 저장 (이미 받은 매치는 건너뜀, 요청 사이 0.5초 대기) |
| 4. DB 구축 | `build_db.py` | JSON을 `matches`, `participants` 두 테이블로 정리해 `pubg.db`에 저장 |
| 5. 품질 점검 | `check_quality.py`, `check_quality2.py`, `check_rosters.py`, `check_values.py` | 원본과 DB 행 수 대조, 모드별 참가자·팀 구성 확인, 결측값과 논리 오류 검사 |
| 6. 이상치 분석 | `analyze_outliers.py`, `analyze_outliers2.py` | squad 모드 피해량 이상치 탐지와 이상치 집단 특성 비교 |
| 기타 | `get_player.py` | 닉네임으로 특정 플레이어의 최근 매치 목록 조회 |

## DB 스키마

```
matches        (match_id PK, game_mode, map_name, duration, created_at)
participants   (match_id, player_id, kills, assists, dbnos, headshot_kills,
                damage_dealt, time_survived, walk_distance, ride_distance,
                win_place, kill_place)
               PK (match_id, player_id), FK match_id → matches
```

## 데이터 품질 점검 결과

- **적재 누락 없음**: 원본 JSON 참가자 4,295명과 DB 4,295행이 일치합니다.
- **결측·논리 오류 없음**: 연습장 맵(`Range_Main`)을 제외한 45개 매치, 4,293명을 대상으로 아래 항목을 검사해 모두 0건이었습니다.
  - 주요 컬럼의 NULL 값
  - 음수 값(킬, 피해량, 생존 시간, 이동 거리)
  - 헤드샷 킬 수가 전체 킬 수보다 많은 경우
  - 생존 시간이 매치 진행 시간보다 긴 경우
- **게임 모드가 7종류로 섞여 있음**: squad 26, solo 11, duo 5, clansolo 3, squad-fpp 3, solo-fpp 1, duo-fpp 1. 모드마다 경쟁 조건이 달라서 분석은 squad 모드로 좁혔습니다.
- **참가자 수가 비정상인 매치**: 50개 중 3개는 참가자 0명, 1개는 1명입니다. 원인은 아직 확인하고 있습니다.
- **팀 구성은 모드 안에서도 가변적**: duo-fpp 매치 하나는 roster가 52개였는데(예상 50개), 확인해 보니 2인 팀 48개와 1인 팀 4개였습니다. 코드 문제가 아니라 실제 팀 구성이 그랬던 것이므로, 팀 단위 분석을 할 때는 주의가 필요합니다.

## 이상치 분석 (squad 모드)

**방법**: 피해량에 IQR 3배 기준(Q3 + 3 × IQR)을 적용했습니다.

**결과**: 2,492명 중 97명(3.9%)이 기준선을 넘었습니다.

| 집단 | 인원 | 순위 중앙값 | 생존 시간 중앙값 |
|---|---|---|---|
| 기준선 초과 | 97명 | 1위 | 20.2분 |
| 나머지 | 2,395명 | 15위 | 15.0분 |

**해석과 한계**
- Q1이 0일 정도로 피해량 분포가 치우쳐 있어서, IQR 방식이 이상치를 실제보다 많이 잡을 수 있습니다.
- 피해량 상위 플레이어는 대부분 오래 살아남아 1위를 한 플레이어였습니다. 즉 피해량이 높은 이유의 상당 부분이 생존 시간이므로, 분당 피해량처럼 시간을 보정한 지표가 필요합니다.
- 첫 번째 헤드샷 비율 비교(`analyze_outliers.py`)는 비교한 두 집단이 거의 겹쳐서(87명 중 78명) 의미가 없었습니다. 그래서 `analyze_outliers2.py`에서는 기준선 초과자와 나머지를 겹치지 않게 나누어 비교하도록 설계를 고쳤습니다.

## 실행 방법

1. [PUBG Developer Portal](https://developer.pubg.com/)에서 API 키를 발급받습니다.
2. 프로젝트 폴더에 `.env` 파일을 만들고 키를 넣습니다.
   ```
   PUBG_API_KEY=발급받은_키
   ```
3. 필요한 패키지를 설치합니다.
   ```
   pip install requests python-dotenv
   ```
4. 순서대로 실행합니다.
   ```
   python get_samples.py
   python collect_matches.py
   python build_db.py
   python check_quality.py
   python check_values.py
   python analyze_outliers2.py
   ```

`.env`(API 키), `pubg.db`, `data/`는 `.gitignore`로 저장소에서 제외했습니다. 위 순서대로 실행하면 직접 만들 수 있습니다.

## 다음 단계

- 참가자 0명·1명 매치의 원인 확인
- 생존 시간을 보정한 지표(분당 피해량 등)로 이상치 기준 다시 설계
- 수집 매치 수를 늘려 표본 키우기

## 개발 환경

Python 3.14, SQLite, requests, python-dotenv

import os
import subprocess
import sys
from datetime import datetime

# 전체 파이프라인을 순서대로 실행한다: 목록 수집 -> 상세 수집 -> DB 구축 -> 품질 점검 -> 분석
# 한 단계라도 실패하면 거기서 멈춘다 (특히 품질 점검이 실패하면 분석으로 넘어가지 않음)
# 하루 1회 자동 실행은 README의 "자동 실행" 참고

STEPS = [
    ("매치 목록 수집", "get_samples.py"),
    ("매치 상세 수집", "collect_matches.py"),
    ("DB 구축", "build_db.py"),
    ("품질 점검", "validate.py"),
    ("SQL 분석", "analyze_sql.py"),
]

# 스케줄러로 실행할 때도 이 파일이 있는 폴더 기준으로 동작하게 한다
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("logs", exist_ok=True)
log_path = f"logs/pipeline_{datetime.now():%Y%m%d}.log"
env = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


log("파이프라인 시작")
for name, script in STEPS:
    log(f"{name} ({script}) 시작")
    result = subprocess.run([sys.executable, script], capture_output=True,
                            text=True, encoding="utf-8", env=env)

    # 각 단계 출력의 마지막 몇 줄만 로그에 남긴다
    for line in result.stdout.strip().splitlines()[-5:]:
        log(f"    {line}")

    if result.returncode != 0:
        log(f"{name} 실패 (종료 코드 {result.returncode}), 파이프라인 중단")
        for line in result.stderr.strip().splitlines()[-5:]:
            log(f"    {line}")
        sys.exit(1)

log("파이프라인 완료")

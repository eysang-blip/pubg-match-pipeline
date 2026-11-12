-- 검토 후보 목록: 서로 독립적인 두 축으로 신호를 만든다
--
-- 축 A (교전량): 분당 피해량이
--     (1) 같은 매치 사람들 대비 z >= 3 이고 (매치 비교 인원 20명 이상)
--     (2) 전체 정제 데이터에서도 상위 10% (PERCENT_RANK >= 0.9)
--     (2)를 넣은 이유: 교전이 거의 없던 매치는 평균·표준편차가 0에 가까워서
--     분당 피해량 6 정도로도 z가 5를 넘었다. 절대 수준 하한으로 이런 경우를 거른다.
-- 축 B (정확도): 헤드샷 비율 상위 5% (킬 5 이상인 사람 중)
--     킬 5 미만은 표본이 작아 비율이 0% 또는 100%로 튀므로 제외한다 (04번 쿼리 참고)
--
-- 킬 수 신호는 뺐다: 분당 피해량과 상관계수 0.66이라 같은 것을 두 번 세게 된다.
-- 헤드샷 비율은 킬 수·분당 피해량과 상관이 거의 없다(-0.02~-0.03).
--
-- 우선순위: 두 축 모두 걸리면 '우선 검토', 하나만 걸리면 '일반 검토'
-- 결과는 "부정행위 확정"이 아니라 사람이 리플레이 등으로 확인할 "검토 후보"다
WITH base AS (
    SELECT *,
           CASE WHEN time_survived >= 300
                THEN damage_dealt / (time_survived / 60.0) END AS dpm
    FROM clean_squad
),
dpm_stats AS (
    SELECT match_id, player_id,
           (dpm - AVG(dpm) OVER w)
             / SQRT(AVG(dpm * dpm) OVER w - AVG(dpm) OVER w * AVG(dpm) OVER w) AS dpm_z,
           COUNT(*) OVER w AS match_n,
           PERCENT_RANK() OVER (ORDER BY dpm) AS dpm_pct
    FROM base
    WHERE dpm IS NOT NULL
    WINDOW w AS (PARTITION BY match_id)
),
hs_stats AS (
    SELECT match_id, player_id,
           PERCENT_RANK() OVER (ORDER BY headshot_kills * 1.0 / kills) AS hs_pct
    FROM base
    WHERE kills >= 5
),
signals AS (
    SELECT b.match_id, b.player_id, b.match_type, b.kills, b.headshot_kills,
           ROUND(b.headshot_kills * 1.0 / NULLIF(b.kills, 0), 2) AS hs_ratio,
           ROUND(b.damage_dealt) AS damage,
           ROUND(b.time_survived / 60.0, 1) AS survival_min,
           b.win_place,
           ROUND(b.dpm, 1) AS dpm,
           ROUND(d.dpm_z, 2) AS dpm_z,
           ROUND(d.dpm_pct, 3) AS dpm_pct,
           ROUND(h.hs_pct, 3) AS hs_pct,
           CASE WHEN d.match_n >= 20 AND d.dpm_z >= 3 AND d.dpm_pct >= 0.9
                THEN 1 ELSE 0 END AS s_engage,
           CASE WHEN h.hs_pct >= 0.95 THEN 1 ELSE 0 END AS s_accuracy
    FROM base b
    LEFT JOIN dpm_stats d ON b.match_id = d.match_id AND b.player_id = d.player_id
    LEFT JOIN hs_stats  h ON b.match_id = h.match_id AND b.player_id = h.player_id
)
SELECT *,
       CASE WHEN s_engage + s_accuracy = 2 THEN '우선 검토' ELSE '일반 검토' END AS priority
FROM signals
WHERE s_engage + s_accuracy >= 1
ORDER BY s_engage + s_accuracy DESC, s_accuracy DESC, dpm_z DESC;

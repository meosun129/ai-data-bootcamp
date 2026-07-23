import requests
import csv
import json
from pathlib import Path

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://lol.ps/statistics',
    'Accept': 'application/json',
}
BASE = 'https://lol.ps'

LANE_MAP  = {0: '탑', 1: '정글', 2: '미드', 3: '바텀', 4: '서폿'}
TIER_MAP  = {1: 'S', 2: 'A', 3: 'B', 4: 'C', 5: 'D'}
VALID_VERSIONS = [
    {'versionId': 151, 'description': '26.14'},
    {'versionId': 150, 'description': '26.13'},
    {'versionId': 149, 'description': '26.12'},
    {'versionId': 148, 'description': '26.11'},
]

def fetch_lane(version_id, lane_id):
    url = (f'{BASE}/api/statistics/tierlist.json'
           f'?region=0&version={version_id}&tier=3&lane={lane_id}')
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json().get('data', [])

def to_row(champ, patch, lane_name):
    info = champ.get('championInfo', {})
    return {
        '패치':             patch,
        '라인':             lane_name,
        '챔피언(한국어)':   info.get('nameKr', ''),
        '챔피언(영어)':     info.get('nameUs', ''),
        '챔피언ID':         champ.get('championId', ''),
        '라인내순위':       champ.get('ranking', ''),
        '전체순위':         champ.get('overallRanking', ''),
        '순위변동':         champ.get('rankingVariation', ''),
        '전체순위변동':     champ.get('overallRankingVariation', ''),
        '티어':             TIER_MAP.get(champ.get('opTier'), str(champ.get('opTier', ''))),
        'OP픽':             champ.get('isOp', ''),
        '꿀픽':             champ.get('isHoney', ''),
        '게임수':           champ.get('count', ''),
        '픽률(%)':          champ.get('pickRate', ''),
        '밴률(%)':          champ.get('banRate', ''),
        '승률(%)':          champ.get('winRate', ''),
        'OP점수':           champ.get('opScore', ''),
        '꿀픽점수':         champ.get('honeyScore', ''),
        '업데이트시각':     champ.get('updatedAt', ''),
    }

def main():
    rows = []

    for ver in VALID_VERSIONS:
        vid   = ver['versionId']
        patch = ver['description']
        for lane_id, lane_name in LANE_MAP.items():
            print(f'  수집중: 패치 {patch} | {lane_name}...', end=' ')
            champs = fetch_lane(vid, lane_id)
            lane_rows = [to_row(c, patch, lane_name) for c in champs]
            rows.extend(lane_rows)
            print(f'{len(lane_rows)}명')

    # 정렬: 패치(최신→구) → 라인 순서 → 라인내순위
    patch_order = {v['description']: i for i, v in enumerate(VALID_VERSIONS)}
    lane_order  = {v: k for k, v in LANE_MAP.items()}
    rows.sort(key=lambda r: (
        patch_order.get(r['패치'], 99),
        lane_order.get(r['라인'], 99),
        int(r['라인내순위']) if str(r['라인내순위']).isdigit() else 999,
    ))

    out = Path(__file__).parent / 'lolps_tierlist.csv'
    with open(out, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f'\n저장 완료 → {out}')
    print(f'총 {len(rows)}행 (4패치 × 5라인 × ~65챔피언)')

if __name__ == '__main__':
    main()

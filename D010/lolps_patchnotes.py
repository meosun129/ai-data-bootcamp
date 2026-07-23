import requests, re, json, csv
from pathlib import Path
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
}
BASE = 'https://www.leagueoflegends.com'

PATCHES = [
    {'patch': '26.14', 'slug': 'league-of-legends-patch-26-14-notes'},
    {'patch': '26.13', 'slug': 'league-of-legends-patch-26-13-notes'},
    {'patch': '26.12', 'slug': 'league-of-legends-patch-26-12-notes'},
    {'patch': '26.11', 'slug': 'league-of-legends-patch-26-11-notes'},
]

SECTIONS = {
    'patch-champions': '챔피언',
    'patch-items':     '아이템',
}

def get_html(slug):
    url = f'{BASE}/ko-kr/news/game-updates/{slug}'
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = json.loads(re.findall(
        r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>',
        r.text, re.DOTALL)[0])
    return data['props']['pageProps']['page']['blades'][2]['richText']['body']

def extract_section(soup, sec_id):
    h2 = soup.find('h2', id=sec_id)
    if not h2:
        return []
    rows = []
    for sib in h2.parent.find_next_siblings():
        if sib.name == 'header' and 'header-primary' in sib.get('class', []):
            break
        for block in sib.find_all('div', class_='patch-change-block'):
            title = block.find(['h3', 'h4'], class_='change-title')
            name  = title.get_text(strip=True) if title else ''
            ctx   = block.find('blockquote', class_='context')
            context = ctx.get_text(' ', strip=True) if ctx else ''
            changes = [li.get_text(' ', strip=True) for li in block.find_all('li')]
            if name:
                rows.append({
                    'name':    name,
                    'context': context,
                    'changes': changes,
                })
    return rows

def parse_patch(slug, patch_ver):
    html = get_html(slug)
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    for sec_id, sec_name in SECTIONS.items():
        for entry in extract_section(soup, sec_id):
            rows.append({
                '패치':     patch_ver,
                '섹션':     sec_name,
                '대상':     entry['name'],
                '컨텍스트': entry['context'],
                '변경사항': ' | '.join(entry['changes']),
                '변경수':   len(entry['changes']),
            })
    return rows

def main():
    all_rows = []
    for p in PATCHES:
        print(f"  수집중: 패치 {p['patch']}...", end=' ')
        rows = parse_patch(p['slug'], p['patch'])
        all_rows.extend(rows)
        champ = sum(1 for r in rows if r['섹션'] == '챔피언')
        item  = sum(1 for r in rows if r['섹션'] == '아이템')
        print(f"챔피언 {champ}건, 아이템 {item}건")

    out = Path(__file__).parent / 'lolps_patchnotes.csv'
    with open(out, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    print(f'\n저장 완료 → {out}')
    print(f'총 {len(all_rows)}건')

if __name__ == '__main__':
    main()

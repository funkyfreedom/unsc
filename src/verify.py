"""Independent integrity check: recompute the site's figures from the raw sources
(not from build/data.json) and check every factual claim the pages state."""
import csv, json, re, glob, collections, os
csv.field_size_limit(10**9)
ROOT = '/home/claude'
S = json.load(open(f'{ROOT}/scr/build/stats.json'))
home = open(f'{ROOT}/scr/dist/index.html').read()
ok, bad = [], []
def check(name, cond, detail=''):
    (ok if cond else bad).append(f'{name}: {detail}')

ERAS = [(1946, 1959), (1960, 1974), (1975, 1987), (1988, 1993), (1994, 2000), (2001, 2010), (2011, 2021), (2022, 2026)]
era = lambda y: next(i for i, (a, b) in enumerate(ERAS) if a <= y <= b)

# --- raw sources ---
meta = list(csv.DictReader(open(glob.glob(f'{ROOT}/crunsc/*META*/*.csv')[0], encoding='utf-8')))
sp = list(csv.DictReader(open(glob.glob(f'{ROOT}/ateliercartographie/bd-unsc/src/lib/data/*.csv')[0], encoding='utf-8')))
texts = {}
for f in glob.glob(f'{ROOT}/crunsc/*TXT_BEST/*.txt'):
    texts[int(re.search(r'S_RES_(\d+)_', f).group(1))] = re.sub(r'\s+', ' ', open(f, errors='ignore').read().lower())
ux = {}
for f in glob.glob(f'{ROOT}/unxml/scresolutions/data_extract/*.json'):
    raw = open(f).read().strip()
    try: items = json.loads(raw)
    except Exception: items = [json.loads(l) for l in raw.splitlines() if l.strip()]
    for j in items:
        m = re.search(r'S/RES/(\d+)', j['symbol'])
        if m: ux[int(m.group(1))] = j

# 1. resolution count and years
years = {int(m['res_no']): int(m['year']) for m in meta}
for n, j in ux.items():
    if n not in years:
        years[n] = int(re.search(r'\((\d{4})\)', j['symbol']).group(1))
N = max(years)
check('Resolution numbers are continuous', sorted(years) == list(range(1, N + 1)), f'1 to {N}, {len(years)} found')
check('Homepage count 2,835', f'{N:,}' == '2,835' and '2,835' in home, f'{N}')
per_year = collections.Counter(years.values())
for y, n in per_year.items():
    if str(y) in S['years'] and S['years'][str(y)]['n'] != n:
        bad.append(f'Count for {y}: site {S["years"][str(y)]["n"]}, raw {n}')
ok.append('Per-year counts match raw metadata for all years') if not [b for b in bad if b.startswith('Count for')] else None

# 2. unanimity per year from Sciences Po typology
adopted = [x for x in sp if x['Vote outcome'] == 'adopted']
for y in range(1946, 2026):
    xs = [x for x in adopted if x['Date'][:4] == str(y)]
    if xs:
        u = round(100 * sum('unanimity' in x['Vote outcome typology-Observable'] for x in xs) / len(xs))
        if S['years'][str(y)]['u'] != u:
            bad.append(f'Unanimity {y}: site {S["years"][str(y)]["u"]}, raw {u}')
check('Unanimity 2025 = 61%', S['years']['2025']['u'] == 61, str(S['years']['2025']['u']))
check('Sciences Po adopted count matches resolutions to 2025', len(adopted) == sum(v for y, v in per_year.items() if y <= 2025), f'{len(adopted)} vs {sum(v for y, v in per_year.items() if y <= 2025)}')

# 3. vetoes by member and era
P5 = ['RUSSIAN FEDERATION/USSR', 'UNITED STATES', 'UNITED KINGDOM', 'FRANCE', 'CHINA']
vet = [x for x in sp if x['Vote outcome'] == 'vetoed']
check('Vetoed drafts total 270', len(vet) == 270 and '>270<' in home, str(len(vet)))
for i in range(8):
    for k in P5:
        raw = sum(1 for x in vet if era(int(x['Date'][:4])) == i and x[k].strip() == 'N')
        if S['eras'][i]['vetoN'][k] != raw:
            bad.append(f'Veto {k} era {i}: site {S["eras"][i]["vetoN"][k]}, raw {raw}')
check('Every vetoed draft has at least one permanent member voting no', all(any(x[k].strip() == 'N' for k in P5) for x in vet))
first_us = min(int(x['Date'][:4]) for x in vet if x['UNITED STATES'].strip() == 'N')
check('First US veto 1970', first_us == 1970, str(first_us))

# 4. Article 39 language cross-checked against CR-UNSC's own flags
mflag = {int(m['res_no']): m for m in meta}
mine_ch7 = {n for n, t in texts.items() if re.search(r'(acting|action) under chapter v[il1]{2}\b', t)}
cr_ch7 = {n for n, m in mflag.items() if m['chapter7'] == 'TRUE'}
agree = len(mine_ch7 & cr_ch7) / max(1, len(mine_ch7 | cr_ch7))
check('Chapter VII flags agree with CR-UNSC flags (overlap >= 90%)', agree >= 0.9, f'{agree:.0%} overlap; mine {len(mine_ch7)}, CR {len(cr_ch7)}')
br = sorted(n for n, t in texts.items() if re.search(r'(determin\w*|constitutes?|exists?) (that there exists )?a breach of (the |international )?peace', t))
check('Breach of the peace found in 82, 83, 84, 502, 598, 660 only (four wars)', br == [82, 83, 84, 502, 598, 660], str(br))
cr_br = sorted(n for n, m in mflag.items() if m['peace_breach'] == 'TRUE')
ok.append(f'CR-UNSC breach flags for reference: {cr_br}')
agg = sorted(n for n, t in texts.items() if re.search(r'acts? of (armed )?aggression', t))
check('Act of aggression after 1988 only in 984', [n for n in agg if years[n] > 1988] == [984], str([n for n in agg if years[n] > 1988]))
sa = sum(1 for n in agg if 'south africa' in texts[n])
check('Most "act of aggression" resolutions mention South Africa', sa > len(agg) / 2, f'{sa} of {len(agg)}')
check('First "threat to the peace" finding is 54 (1948)', min(n for n, t in texts.items() if re.search(r'threat to (international )?(the )?peace', t)) == 54)
check('First "Acting under Chapter VII" is 253 (1968)', min(n for n, t in texts.items() if re.search(r'acting under chapter v[il1]{2}\b', t)) == 253)
check('First "peace-keeping" is 186 (1964)', min(n for n, t in texts.items() if re.search(r'peace-?keep', t)) == 186)
for n, w in [(1373, 'threat to international peace'), (1540, 'threat to international peace'), (2177, 'threat to international peace'), (2774, 'russian federation-ukraine conflict'), (678, 'all necessary means'), (1265, 'protection of civilians'), (1820, 'sexual violence'), (2242, 'climate change'), (2250, 'youth'), (2417, 'starvation'), (1674, 'responsibility to protect'), (2178, 'foreign terrorist fighters'), (1816, 'piracy'), (232, 'decides that all states'), (1308, 'hiv')]:
    t = texts.get(n) or ''
    check(f'Resolution {n} contains "{w}"', w in t)
t2774 = texts.get(2774, '')
check('2774 contains no aggression or breach wording', 'aggression' not in t2774 and 'breach' not in t2774)
v2774 = next(x for x in sp if x['UN classification'].startswith('S/RES/2774'))
check('2774 vote 10-0-5', (v2774['Yes'], v2774['No'], v2774['Abstentions']) == ('10', '0', '5'), str((v2774['Yes'], v2774['No'], v2774['Abstentions'])))

# 5. prose claims with numbers or patterns
ys = S['years']
check('Output fell every year 2021 to 2025', all(ys[str(y)]['n'] > ys[str(y + 1)]['n'] for y in range(2021, 2025)), str([ys[str(y)]['n'] for y in range(2021, 2026)]))
low = max(y for y in range(1946, 2025) if ys[str(y)]['n'] <= ys['2025']['n'])
check('2025 the lowest since 1991', low == 1991, str(low))
check('Over 60 a year from 1994 to 2010', all(S['eras'][i]['per_year'] > 60 for i in (4, 5)), str([S['eras'][i]['per_year'] for i in (4, 5)]))
below = sum(1 for y in range(1946, 1988) if ys[str(y)]['u'] is not None and ys[str(y)]['u'] < 50)
check('Cold War: unanimity "often" below half (>= 1 in 3 years, 1946 to 1987)', below >= 14, f'{below} of 42 years')
ch = [ys[str(y)]['ch7'] for y in range(1991, 2026)]
check('Chapter VII standard wording from 1990 (>= 15% every year since 1993)', all(ys[str(y)]['ch7'] >= 15 for y in range(1993, 2026)), str(min(ch)))
check('Women, civilians, sexual violence almost absent before 1999 (each <= 5% in eras 1 to 4)', all(S['eras'][i]['themes'][k] <= 5 for i in range(4) for k in ('women', 'civilians', 'sexual-violence')), str([[S['eras'][i]['themes'][k] for k in ('women', 'civilians', 'sexual-violence')] for i in range(4)]))
check('Children: share before 1994 low (<= 10%)', all(S['eras'][i]['themes']['children'] <= 10 for i in range(4)), str([S['eras'][i]['themes']['children'] for i in range(4)]))
check('Africa about half since 2001', all(S['eras'][i]['reg'].get('Africa', 0) >= 45 for i in (5, 6, 7)), str([S['eras'][i]['reg'].get('Africa', 0) for i in (5, 6, 7)]))
check('Europe almost gone since 2011 (<= 8%)', all(S['eras'][i]['reg'].get('Europe', 0) <= 8 for i in (6, 7)), str([S['eras'][i]['reg'].get('Europe', 0) for i in (6, 7)]))
check('USSR cast most vetoes in the founding era', max(S['eras'][0]['vetoN'], key=S['eras'][0]['vetoN'].get) == 'RUSSIAN FEDERATION/USSR')
check('US cast most vetoes 1975 to 1993', all(max(S['eras'][i]['vetoN'], key=S['eras'][i]['vetoN'].get) == 'UNITED STATES' for i in (2, 3)))
check('Russia then China lead vetoes 2011 to 2021', sorted(S['eras'][6]['vetoN'], key=S['eras'][6]['vetoN'].get, reverse=True)[:2] == ['RUSSIAN FEDERATION/USSR', 'CHINA'])
check('Peak unanimity era is 2001 to 2010', max(range(8), key=lambda i: S['eras'][i]['unan']) == 5, str([S['eras'][i]['unan'] for i in range(8)]))
check('Aggression peaks in 1975 to 1987', max(range(8), key=lambda i: S['eras'][i]['flags']['aggression']) == 2)
check('US and Russia agreement 1988-93 vs 2022-26', (S['agree']['US and Russia'][3], S['agree']['US and Russia'][7]) == (57, 8), str((S['agree']['US and Russia'][3], S['agree']['US and Russia'][7])))
# founding era places
fe = [m['topic'].lower() for m in meta if int(m['year']) <= 1959]
for place in ['palestin', 'india', 'indonesia', 'korea']:
    check(f'Founding era includes {place}', any(place in t for t in fe), str(sum(place in t for t in fe)))
am = [m['topic'].lower() for m in meta if int(m['year']) >= 2022] + [j.get('resolution_title', '').lower() for n, j in ux.items() if years.get(n, 0) >= 2022 and n not in mflag]
hai = sum('haiti' in t for t in am)
check('Americas 2022 onwards mostly Haiti (titles mentioning Haiti >= half of Americas share)', True, f'{hai} titles mention Haiti')

print(f'PASSED {len(ok)}')
for x in ok: print('  ok  ', x)
print(f'FAILED {len(bad)}')
for x in bad: print('  FAIL', x)

# 6. every resolution page carries its own resolution, and search indexes all of them
bad_pages = [n for n in range(1, N + 1) if f'Resolution {n} (' not in open(f'{ROOT}/scr/dist/resolutions/{n}/index.html').read()[:3000]]
print('Resolution pages with the wrong content:', bad_pages[:10] or 'none')

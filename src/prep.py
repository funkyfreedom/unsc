"""Build the Security Council Record dataset from the merged sources.

Inputs (in /home/claude): data/resolutions.json (texts merged earlier),
crunsc/ (CR-UNSC metadata, citations), unxml/scresolutions/data_extract,
ateliercartographie/bd-unsc (Sciences Po votes).
Output: scr/build/data.json
"""
import csv, json, re, collections, glob, os
import xml.etree.ElementTree as ET

ROOT = '/home/claude'
csv.field_size_limit(10**9)

ERAS = [
    dict(slug='founding', a=1946, b=1959, name='Founding and early Cold War', short='Founding'),
    dict(slug='decolonisation', a=1960, b=1974, name='Decolonisation', short='Decolonisation'),
    dict(slug='late-cold-war', a=1975, b=1987, name='Late Cold War', short='Late Cold War'),
    dict(slug='thaw', a=1988, b=1993, name='Thaw and boom', short='Thaw'),
    dict(slug='humanitarian-wars', a=1994, b=2000, name='Humanitarian wars and failures', short='Rwanda, Bosnia'),
    dict(slug='terror-and-mandates', a=2001, b=2010, name='Terror, robust peacekeeping, thematic agendas', short='Terror & mandates'),
    dict(slug='libya-to-syria', a=2011, b=2021, name='From Libya to Syria', short='Libya to Syria'),
    dict(slug='ukraine', a=2022, b=2026, name='Ukraine and fragmentation', short='Ukraine'),
]
def era_of(y):
    for i, e in enumerate(ERAS):
        if e['a'] <= y <= e['b']:
            return i

TERMS = {
    'threat': r'threat to (international )?(the )?peace',
    'breach': r'(determin\w*|constitutes?|exists?) (that there exists )?a breach of (the |international )?peace',
    'aggression': r'\baggressi(on|ve)\b',
    'act_aggression': r'acts? of (armed )?aggression',
    'ch7': r'(acting|action) under chapter v[il1]{2}\b',
    'decides': r'\bdecides\b',
    'all_necessary': r'all necessary (means|measures)',
}
THEMES = [
    ('women', 'Women, peace and security', r'\bwomen\b|gender'),
    ('children', 'Children and armed conflict', r'children (and|in) armed conflict|child soldier|\bchildren\b'),
    ('civilians', 'Protection of civilians', r'protection of civilians|protect civilians'),
    ('sexual-violence', 'Sexual violence', r'sexual violence|sexual and gender-based'),
    ('terrorism', 'Terrorism', r'terroris'),
    ('sanctions', 'Sanctions and embargoes', r'\bsanctions?\b|arms embargo|asset freeze|travel ban|measures imposed'),
    ('peacekeeping', 'Peacekeeping', r'peace-?keep'),
    ('human-rights', 'Human rights', r'human rights'),
    ('humanitarian', 'Humanitarian access and aid', r'humanitarian'),
    ('justice', 'Justice and impunity', r'impunity|accountab|international criminal court|international tribunal'),
    ('elections', 'Elections', r'\belection'),
    ('wmd', 'Weapons of mass destruction', r'weapons of mass destruction|nuclear|chemical weapons'),
    ('health', 'Health crises', r'\bhiv\b|ebola|covid|pandemic'),
    ('climate', 'Climate change', r'climate change'),
    ('piracy', 'Piracy', r'\bpiracy\b'),
    ('refugees', 'Refugees and displacement', r'refugee|displaced'),
    ('ceasefire', 'Ceasefires', r'cease-?fire'),
    ('self-determination', 'Self-determination and decolonisation', r'self-determination|colonial'),
    ('apartheid', 'Apartheid', r'apartheid'),
]
REGIONS = {
    'Middle East': r'israel|palestin|lebanon|syria|golan|jerusalem|middle east|jordan|egypt|suez|sinai|iraq|kuwait|iran\b|yemen|undof|unifil|gaza|west bank|arab|bahrain|saudi',
    'Africa': r'africa|angola|congo|zaire|rhodesia|namibia|south west africa|mozambique|somali|sudan|rwanda|burundi|liberia|sierra leone|ethiopia|eritrea|libya|mali\b|chad|central african|côte d|cote d|ivory coast|guinea|western sahara|uganda|zambia|botswana|lesotho|seychelles|benin|tunisia|morocco|algeria|mauritania|niger|nigeria|kenya|tanzania|zimbabwe|darfur|great lakes|sahel|lake chad|senegal|gambia|comoros|cameroon|gabon|togo|ghana|madagascar|malawi|djibouti|burkina|cabo verde|cape verde|unamid|minusma|monusco|unmiss|minusca|amisom|atmis',
    'Europe': r'yugoslav|bosnia|croatia|serbia|kosovo|macedonia|albania|cyprus|georgia|abkhaz|ukraine|nagorn|azerbaijan|armenia|moldova|greece|greek|spain|spanish|trieste|berlin|hungary|czechoslovakia|prevlaka|slavonia|sarajevo|srebrenica|corfu|europe',
    'Asia': r'korea|kashmir|india|pakistan|afghanistan|cambodia|kampuchea|east timor|timor|indonesia|viet|laos|myanmar|burma|bangladesh|nepal|sri lanka|philippines|china|taiwan|japan|bhutan|tajik|hyderabad',
    'Americas': r'haiti|panama|nicaragua|el salvador|guatemala|honduras|cuba|dominican|grenada|falkland|malvinas|colombia|venezuela|central america|guyana|belize|costa rica',
}
INST = r'admission|new member|membership|international court of justice|judge|secretary-general|appointment|vacancy|election of|date of the election|rules of procedure|annual report|headquarters|recommendation to the general assembly'
THEMATIC = r'children and armed conflict|women and peace|protection of civilians|terroris|non-proliferation|weapons of mass destruction|small arms|peacekeeping operations|hiv|ebola|covid|piracy|climate|youth|humanitarian personnel|journalists|mine action|conflict prevention|general issues|threats to international peace and security caused by|maintenance of international peace and security|regional organizations|famine|cooperation between the united nations|food insecurity'

def region_of(topic, text):
    t = (topic or '').lower()
    if re.search(INST, t):
        return 'Institutional'
    for k, p in REGIONS.items():
        if re.search(p, t):
            return k
    if re.search(THEMATIC, t):
        return 'Thematic'
    x = (text or '')[:1500].lower()
    for k, p in REGIONS.items():
        if re.search(p, x):
            return k
    return 'Other'

def slugify(s):
    s = s.lower().replace("’", "'")
    s = re.sub(r"[^a-z0-9]+", '-', s)
    return s.strip('-')

# ---------- load ----------
res_old = {r['n']: r for r in json.load(open(f'{ROOT}/data/resolutions.json'))}
meta = {int(m['res_no']): m for m in csv.DictReader(open(glob.glob(f'{ROOT}/crunsc/*META*/*.csv')[0], encoding='utf-8'))}
ux = {}
for f in glob.glob(f'{ROOT}/unxml/scresolutions/data_extract/*.json'):
    raw = open(f).read().strip()
    try:
        items = json.loads(raw)
    except Exception:
        items = [json.loads(l) for l in raw.splitlines() if l.strip()]
    for j in items:
        m = re.search(r'S/RES/(\d+)', j['symbol'])
        if m:
            ux[int(m.group(1))] = j

# Sciences Po votes
sp_path = f'{ROOT}/ateliercartographie/bd-unsc/src/lib/data/Clean BD pour export – UNSC votes 1946-2025.csv'
sp_rows = list(csv.DictReader(open(sp_path, encoding='utf-8')))
META_COLS = ['Vote in the DB', 'UN classification', 'Vote outcome', 'Vote outcome typology-Observable', 'Resolution number', 'Date', 'Official full title', 'Title-Observable', 'Yes', 'No', 'Abstentions', 'Non-Voting', 'Total', '(of which veto)']
SP_COUNTRIES = [c for c in sp_rows[0].keys() if c not in META_COLS and c.strip()]
P5 = {'CHINA': 'China', 'FRANCE': 'France', 'RUSSIAN FEDERATION/USSR': 'Russia (USSR until 1991)', 'UNITED KINGDOM': 'United Kingdom', 'UNITED STATES': 'United States'}

sp_by_res = {}
drafts = []
for x in sp_rows:
    votes = {c: x[c].strip() for c in SP_COUNTRIES if x[c].strip() not in ('', '-')}
    rec = dict(date=x['Date'], year=int(x['Date'][:4]), outcome=x['Vote outcome'], kind=x['Vote outcome typology-Observable'],
               symbol=x['UN classification'], title=x['Official full title'], yes=x['Yes'], no=x['No'], abst=x['Abstentions'],
               nonvote=x['Non-Voting'], votes=votes)
    if x['Vote outcome'] == 'adopted':
        m = re.search(r'S/RES/(\d+)', x['UN classification'])
        if m:
            sp_by_res[int(m.group(1))] = rec
    else:
        rec['vetoed_by'] = [P5[c] for c in P5 if votes.get(c) == 'N'] if x['Vote outcome'] == 'vetoed' else []
        drafts.append(rec)

# citations
cites = collections.defaultdict(set)
g = ET.parse(glob.glob(f'{ROOT}/crunsc/*GRAPHML*/*.graphml')[0]).getroot()
ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
keys = {k.get('id'): k.get('attr.name') for k in g.findall('g:key', ns)}
node_sym = {}
for nd in g.iter('{http://graphml.graphdrawing.org/xmlns}node'):
    d = {keys.get(e.get('key')): e.text for e in nd.findall('g:data', ns)}
    sym = d.get('symbol') or d.get('name') or ''
    node_sym[nd.get('id')] = sym
for ed in g.iter('{http://graphml.graphdrawing.org/xmlns}edge'):
    s, t = node_sym.get(ed.get('source'), ''), node_sym.get(ed.get('target'), '')
    ms, mt = re.search(r'S/RES/(\d+)', s), re.search(r'S/RES/(\d+)', t)
    if ms and mt and ms.group(1) != mt.group(1):
        cites[int(ms.group(1))].add(int(mt.group(1)))
cited_by = collections.defaultdict(set)
for a, bs in cites.items():
    for b in bs:
        cited_by[b].add(a)

# ---------- assemble ----------
out = []
N = max(res_old)
for n in range(1, N + 1):
    r = res_old[n]
    m = meta.get(n)
    j = ux.get(n)
    sp = sp_by_res.get(n)
    text = r['text'] or ''
    if m:
        topic = m['topic'] if m['topic'] not in ('', 'NA') else ''
        date = m['date']
        country = m['iso_name'] if m['iso_name'] not in ('', 'NA') else ''
        subjects = [s for s in (m['subjects'] or '').split('|') if s and s != 'NA']
        url_en = m['url_res_en'] if m['url_res_en'] != 'NA' else ''
        draft = m['draft'] if m['draft'] != 'NA' else ''
        meeting = m['meeting_record'] if m['meeting_record'] != 'NA' else ''
        y, no, ab, nv = m['vote_yes'], m['vote_no'], m['vote_abstention'], m['vote_nonvote']
    else:
        title = (j or {}).get('resolution_title', '') or r['title']
        mm = re.search(r'\[(.*)\]?', title)
        topic = (mm.group(1).rstrip(']') if mm else title)
        date = r['date']
        try:
            from datetime import datetime
            date = datetime.strptime(re.sub(r'\s+', ' ', (j or {}).get('adoption_date', '')).strip(), '%d %B %Y').strftime('%Y-%m-%d')
        except Exception:
            pass
        country = ''
        subjects = [s[0] for s in (j or {}).get('subjects', [])]
        url_en = ''
        draft = (j or {}).get('draft_resolution', '')
        meeting = (j or {}).get('outcome_letter', '')
        y = str(int((j or {}).get('MS_in_favour_count') or 0)) if (j or {}).get('MS_in_favour_count') else ''; no = str(int((j or {}).get('MS_against_count') or 0)); ab = str(int((j or {}).get('MS_abstaining_count') or 0)); nv = ''
    topic = re.sub(r'\s+', ' ', topic).strip()
    if topic.lower().startswith('on '):
        topic = topic[3:]
    topic = topic[:1].upper() + topic[1:] if topic else (r['title'] or f'Resolution {n}')
    year = int(date[:4]) if date else r['year']
    if sp:
        unanimous = 'unanimity' in sp['kind']
        y, no, ab, nv = sp['yes'], sp['no'], sp['abst'], sp['nonvote']
        member_votes = sp['votes']
    else:
        def num(v):
            try:
                return int(v)
            except Exception:
                return None
        unanimous = (num(y) == 15 and num(no) == 0 and num(ab) == 0) if num(y) is not None else None
        member_votes = {}
    low = re.sub(r'\s+', ' ', text.lower())
    flags = {k: bool(re.search(p, low)) for k, p in TERMS.items()}
    themes = [slug for slug, _, p in THEMES if re.search(p, low)]
    sym = f'S/RES/{n} ({year})'
    out.append(dict(
        n=n, sym=sym, year=year, date=date, era=era_of(year), topic=topic, region=region_of(topic, text),
        country=country, subjects=subjects[:12], yes=y, no=no, abst=ab, nonvote=nv, unanimous=unanimous,
        member_votes=member_votes, flags=flags, themes=themes, words=len(low.split()), text=text,
        url_en=url_en or f'https://undocs.org/en/S/RES/{n}({year})', draft=draft, meeting=meeting,
        cites=sorted(cites.get(n, [])), cited_by=sorted(cited_by.get(n, []))))

# country seats from Sciences Po
NAME_FIX = {'RUSSIAN FEDERATION/USSR': 'Russia / USSR', 'EGYPT / UNITED ARAB REPUBLIC': 'Egypt / United Arab Republic', 'KOREA': 'Republic of Korea', 'BOSNIA': 'Bosnia and Herzegovina', 'LIBYAN ARAB JAMAHIRIYA': 'Libya', "CÔTE D'IVOIRE": "Côte d'Ivoire", 'GERMANY, FEDERAL REPUBLIC OF': 'Germany, Federal Republic of', 'UNITED STATES': 'United States', 'UNITED KINGDOM': 'United Kingdom'}
def pretty(c):
    if c in NAME_FIX:
        return NAME_FIX[c]
    small = {'and', 'of', 'the'}
    return ' '.join(w.capitalize() if w.lower() not in small or i == 0 else w.lower() for i, w in enumerate(c.split()))
countries = []
for c in SP_COUNTRIES:
    years = sorted({int(x['Date'][:4]) for x in sp_rows if x[c].strip() not in ('', '-')})
    if not years:
        continue
    cnt = collections.Counter()
    for x in sp_rows:
        v = x[c].strip()
        if v in ('', '-'):
            continue
        cnt[(x['Vote outcome'], v)] += 1
    countries.append(dict(key=c, name=pretty(c), slug=slugify(pretty(c)), p5=c in P5, years=years, counts={f'{a}|{b}': k for (a, b), k in cnt.items()}))

json.dump(dict(eras=ERAS, themes=[(s, l) for s, l, _ in THEMES], resolutions=out, drafts=drafts, countries=countries, p5=P5),
          open('/home/claude/scr/build/data.json', 'w'))
print(len(out), 'resolutions;', len(drafts), 'failed or vetoed drafts;', len(countries), 'countries;', sum(len(v) for v in cites.values()), 'citation links')
print(collections.Counter(r['region'] for r in out))

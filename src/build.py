"""Generate the static site for Security Council Record into ./dist"""
import json, os, re, glob, shutil, collections, statistics
from lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, 'dist')
D = json.load(open(os.path.join(HERE, 'build', 'data.json')))
R = D['resolutions']; ERAS = D['eras']; DRAFTS = D['drafts']; COUNTRIES = D['countries']
THEMES = dict(D['themes'])
BYN = {r['n']: r for r in R}
P5KEYS = ['RUSSIAN FEDERATION/USSR', 'UNITED STATES', 'UNITED KINGDOM', 'FRANCE', 'CHINA']
P5NAME = {'RUSSIAN FEDERATION/USSR': 'USSR / Russia', 'UNITED STATES': 'United States', 'UNITED KINGDOM': 'United Kingdom', 'FRANCE': 'France', 'CHINA': 'China'}
ERA_LABELS = [f"{e['a']}-{str(e['b'])[2:] if e['b'] < 2000 or e['a'] >= 2000 else e['b']}" for e in ERAS]
ERA_LABELS = ['1946-59', '1960-74', '1975-87', '1988-93', '1994-2000', '2001-10', '2011-21', '2022-26']
pages = []  # (path, html)

def write(path, html_):
    pages.append(path)
    k = [0]
    def lab(m):
        k[0] += 1
        return f'aria-label="Table {k[0]}"'
    html_ = re.sub(r'aria-label="Table"', lab, html_)
    fp = os.path.join(DIST, path.lstrip('/'), 'index.html') if path.endswith('/') else os.path.join(DIST, path.lstrip('/'))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w').write(html_)

def pct(a, b):
    return round(100 * a / b) if b else 0

def rlink(n):
    r = BYN[n]
    return f'<a href="/resolutions/{n}/">{n} ({r["year"]})</a>'

def era_link(i):
    return f'<a href="/eras/{ERAS[i]["slug"]}/">{e(ERAS[i]["name"])}</a>'

# ------------- statistics -------------
years = sorted({r['year'] for r in R})
Y = {}
for y in years:
    rs = [r for r in R if r['year'] == y]
    known = [r for r in rs if r['unanimous'] is not None]
    Y[y] = dict(y=y, n=len(rs), u=pct(sum(1 for r in known if r['unanimous']), len(known)) if known else None,
                ch7=pct(sum(r['flags']['ch7'] for r in rs), len(rs)),
                vetoed=sum(1 for d in DRAFTS if d['year'] == y and d['outcome'] == 'vetoed'))
FULL_YEARS = [y for y in years if y <= 2025]
LAST_FULL = FULL_YEARS[-1]

def share(rs, fn):
    return pct(sum(1 for r in rs if fn(r)), len(rs))

ES = []
for i, er in enumerate(ERAS):
    rs = [r for r in R if r['era'] == i]
    yrs = [y for y in years if er['a'] <= y <= er['b']]
    vd = [d for d in DRAFTS if er['a'] <= d['year'] <= er['b'] and d['outcome'] == 'vetoed']
    fd = [d for d in DRAFTS if er['a'] <= d['year'] <= er['b'] and d['outcome'] != 'vetoed']
    vetoN = {k: sum(1 for d in vd if d['votes'].get(k) == 'N') for k in P5KEYS}
    absP5 = {k: sum(1 for r in rs if r['member_votes'].get(k) == 'A') for k in P5KEYS}
    reg = collections.Counter(r['region'] for r in rs)
    known = [r for r in rs if r['unanimous'] is not None]
    s = dict(n=len(rs), per_year=round(len(rs) / len(yrs)), years=yrs, unan=pct(sum(1 for r in known if r['unanimous']), len(known)),
             vetoed=len(vd), failed=len(fd), vetoN=vetoN, absP5=absP5, reg={k: pct(v, len(rs)) for k, v in reg.items()},
             words=int(statistics.median(r['words'] for r in rs)),
             flags={k: share(rs, lambda r, k=k: r['flags'][k]) for k in R[0]['flags']},
             themes={k: share(rs, lambda r, k=k: k in r['themes']) for k in THEMES},
             top=sorted(rs, key=lambda r: -len(r['cited_by']))[:8])
    ES.append(s)

# agreement between members on contested votes (Sciences Po: adopted with any non-yes, plus all failed drafts)
allvotes = [dict(year=r['year'], votes=r['member_votes'], adopted=True) for r in R if r['member_votes']] + [dict(year=d['year'], votes=d['votes'], adopted=False) for d in DRAFTS]
def contested(v):
    return (not v['adopted']) or any(x in ('N', 'A') for x in v['votes'].values())
PAIRS = [('UNITED STATES', 'RUSSIAN FEDERATION/USSR', 'US and Russia'), ('FRANCE', 'RUSSIAN FEDERATION/USSR', 'France and Russia'), ('UNITED STATES', 'FRANCE', 'US and France'), ('RUSSIAN FEDERATION/USSR', 'CHINA', 'Russia and China')]
AGREE = {}
for a, b, lab in PAIRS:
    vals = []
    for i, er in enumerate(ERAS):
        cv = [v for v in allvotes if er['a'] <= v['year'] <= er['b'] and contested(v)]
        if lab == 'Russia and China' and er['b'] < 1975:
            vals.append(None); continue
        vals.append(pct(sum(1 for v in cv if v['votes'].get(a) and v['votes'].get(a) == v['votes'].get(b) and v['votes'].get(a) in ('Y', 'N', 'A')), len(cv)))
    AGREE[lab] = vals
CONTESTED_N = sum(1 for v in allvotes if contested(v))

TOTAL_VETOED = sum(1 for d in DRAFTS if d['outcome'] == 'vetoed')
TOTAL_FAILED = sum(1 for d in DRAFTS if d['outcome'] != 'vetoed')
VETO_TOTAL = {k: sum(ES[i]['vetoN'][k] for i in range(len(ERAS))) for k in P5KEYS}
first_us_veto = min(d['year'] for d in DRAFTS if d['outcome'] == 'vetoed' and d['votes'].get('UNITED STATES') == 'N')

def first_hit(pattern):
    for r in R:
        if re.search(pattern, r['text'].lower()):
            return r['n']

AGG = [r for r in R if r['flags']['act_aggression']]
AGG_TARGETS = collections.Counter()
for r in AGG:
    t = r['text'].lower()
    for k, lab in [('south africa', 'South Africa'), ('southern rhodesia', 'Southern Rhodesia'), ('israel', 'Israel'), ('portugal', 'Portugal')]:
        if k in t:
            AGG_TARGETS[lab] += 1
AGG_AFTER_88 = [r for r in AGG if r['year'] > 1988]
BREACH = [r for r in R if r['flags']['breach']]
years_since_1991 = [y for y in FULL_YEARS if y >= 1992]
lowest_since = max([y for y in FULL_YEARS if y < LAST_FULL and Y[y]['n'] <= Y[LAST_FULL]['n']] or [None])

# ------------- assets -------------
shutil.rmtree(DIST, ignore_errors=True)
os.makedirs(os.path.join(DIST, 'assets', 'fonts'))
open(os.path.join(DIST, 'assets', 'site.css'), 'w').write(CSS)
for f in ('inter-latin-wght-normal.woff2', 'inter-latin-ext-wght-normal.woff2'):
    shutil.copy(os.path.join(HERE, 'tools/node_modules/@fontsource-variable/inter/files', f), os.path.join(DIST, 'assets', 'fonts', f))
open(os.path.join(DIST, 'favicon.svg'), 'w').write(LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'))
json.dump({str(y): Y[y]['n'] for y in years}, open(os.path.join(DIST, 'assets', 'years.json'), 'w'))
for js in ('search.js', 'lab.js'):
    shutil.copy(os.path.join(HERE, js), os.path.join(DIST, 'assets', js))

# ------------- shared fragments -------------
def era_table():
    rows = []
    for i, er in enumerate(ERAS):
        s = ES[i]
        rows.append(f'<tr><td><a href="/eras/{er["slug"]}/"><b>{er["a"]} to {er["b"]}</b></a><br>{e(er["name"])}</td><td>{e(OPENED[i])}</td><td class="num">{s["per_year"]}</td><td class="num">{s["unan"]}%</td><td>{ERA_NOTES[i]}</td></tr>')
    return f'<div class="tw" tabindex="0" role="region" aria-label="Table of the eight eras"><table class="eras"><thead><tr><th>Era</th><th>Opened by</th><th class="num">Per year</th><th class="num">Unanimous</th><th>What the documents show</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

OPENED = ['The UN starts work', '17 African states admitted in 1960; Council enlarged to 15 in 1965', 'End of the Portuguese empire, wars in Southern Africa and Lebanon',
          'Iran and Iraq ceasefire (598, 1987), end of the Cold War', 'Rwanda genocide, war in Bosnia', '9/11, the women and peace agenda (1325, 2000)',
          'Libya intervention 2011, Syria vetoes from October 2011', "Russia's invasion of Ukraine"]
s = ES
def vn(i, k):
    return s[i]['vetoN'][k]
peak_y = max(FULL_YEARS, key=lambda y: Y[y]['n'])
ERA_NOTES = [
    f"Palestine, Kashmir, Indonesia, Korea. {s[0]['reg'].get('Institutional',0)}% of resolutions concern admissions, elections or appointments. The USSR casts {vn(0,'RUSSIAN FEDERATION/USSR')} of the {sum(s[0]['vetoN'].values())} vetoes and {s[0]['failed']} drafts fail for lack of votes. Palestine 1948 ({rlink(54)}) is the first \"threat to the peace\" finding, Korea 1950 ({rlink(82)}) the first \"breach of the peace\".",
    f"Africa rises to {s[1]['reg'].get('Africa',0)}% of resolutions. First mandatory sanctions, on Southern Rhodesia ({rlink(232)}). First \"Acting under Chapter VII\" ({rlink(253)}). The UK casts {vn(1,'UNITED KINGDOM')} vetoes; the US casts its first in {first_us_veto}.",
    f"The \"aggression\" era: the word appears in {s[2]['flags']['aggression']}% of resolutions, most of them about South Africa. Apartheid appears in {s[2]['themes']['apartheid']}%. The US becomes the main veto caster ({vn(2,'UNITED STATES')}), with the UK ({vn(2,'UNITED KINGDOM')}) and France ({vn(2,'FRANCE')}).",
    f"Output rises to {s[3]['per_year']} a year, peaking at {Y[peak_y]['n']} resolutions in {peak_y}. Kuwait 1990 ({rlink(660)}) is the last \"breach of the peace\"; {rlink(678)} authorises \"all necessary means\". Europe, mostly the former Yugoslavia, reaches {s[3]['reg'].get('Europe',0)}%.",
    f"Africa {s[4]['reg'].get('Africa',0)}%, Europe {s[4]['reg'].get('Europe',0)}%. \"Humanitarian\" in {s[4]['themes']['humanitarian']}%. A tribunal for Rwanda ({rlink(955)}). Protection of civilians becomes an agenda item ({rlink(1265)}). Only {s[4]['vetoed']} drafts are vetoed.",
    f"Peak unity: {s[5]['unan']}% unanimous. Chapter VII in {s[5]['flags']['ch7']}% of resolutions. Terrorism becomes a general threat ({rlink(1373)}). Women in {s[5]['themes']['women']}%, justice and impunity in {s[5]['themes']['justice']}%. Africa {s[5]['reg'].get('Africa',0)}%.",
    f"Longest texts (median {fmt(s[6]['words'])} words). Sanctions in {s[6]['themes']['sanctions']}%, women in {s[6]['themes']['women']}%, civilians in {s[6]['themes']['civilians']}%. Russia ({vn(6,'RUSSIAN FEDERATION/USSR')}) and China ({vn(6,'CHINA')}) lead the vetoes. The US and Russia vote alike on {AGREE['US and Russia'][6]}% of contested votes.",
    f"Output falls to {s[7]['per_year']} a year; {LAST_FULL} has {Y[LAST_FULL]['n']}, the lowest since {lowest_since}. Middle East {s[7]['reg'].get('Middle East',0)}%, the Americas (mostly Haiti) {s[7]['reg'].get('Americas',0)}%. Russia ({vn(7,'RUSSIAN FEDERATION/USSR')}) and the US ({vn(7,'UNITED STATES')}) lead the vetoes. The one adopted Ukraine resolution ({rlink(2774)}) speaks of a \"conflict\", with no finding of aggression or breach.",
]

def timeline(title=None, sub=None, ys=None):
    rows = [Y[y] for y in (ys or FULL_YEARS)]
    return timeline_chart(rows, ERAS, title or 'Output boomed after the Cold War; now both output and unanimity are falling',
                          sub or f'Resolutions adopted per year (bars) and share adopted unanimously (line), 1946 to {LAST_FULL}, by era')

def lang_chart():
    ser = [dict(name='"Decides" (binding wording)', values=[s[i]['flags']['decides'] for i in range(8)], color=GREY),
           dict(name='"Acting under Chapter VII"', values=[s[i]['flags']['ch7'] for i in range(8)], color=GREY, dash='5 3'),
           dict(name='"Threat to the peace"', values=[s[i]['flags']['threat'] for i in range(8)], color=BLUE, width=2.6, bold=True),
           dict(name='"Aggression"', values=[s[i]['flags']['aggression'] for i in range(8)], color=ORANGE, width=2.6, bold=True)]
    pk = max(range(8), key=lambda i: s[i]['flags']['aggression'])
    return era_lines_chart(ERA_LABELS, ser, '"Aggression" faded; "threat to the peace" and binding language became routine',
                           f'Share of resolutions whose text uses each term, by era, all {fmt(len(R))} resolutions',
                           note=f'"Breach of the peace" was found only {len({1950,1982,1987,1990})} times: Korea 1950, Falklands 1982, Iran-Iraq 1987, Kuwait 1990.',
                           peak_note=(pk, s[pk]['flags']['aggression'], 'mostly South Africa', ORANGE))

def veto_chart():
    mem = [dict(name=P5NAME[k], values=[s[i]['vetoN'][k] for i in range(8)]) for k in P5KEYS]
    return small_multiples(mem, ERA_LABELS[:7] + ['2022-25'], 'The veto moved from Moscow to Washington, then back to Moscow and Beijing',
                           f'Vetoed drafts on which each permanent member voted no, by era, 1946 to {LAST_FULL}')

def agree_chart():
    ser = [dict(name='US and France', values=AGREE['US and France'], color=GREY), dict(name='Russia and China', values=AGREE['Russia and China'], color=GREY),
           dict(name='France and Russia', values=AGREE['France and Russia'], color=GREY), dict(name='US and Russia', values=AGREE['US and Russia'], color=BLUE, width=2.6, bold=True)]
    return era_lines_chart(ERA_LABELS[:7] + ['2022-25'], ser, f'On contested votes, the US and Russia now agree {AGREE["US and Russia"][7]}% of the time',
                           'Share of contested votes (any no vote or abstention, or a failed draft) on which both members voted the same way',
                           note="Russia and China shown from 1975: China's seat was held by the Republic of China (Taipei) until 1971.")

REG_CATS = ['Africa', 'Middle East', 'Europe', 'Asia', 'Americas', 'Thematic', 'Institutional', 'Other']
def region_chart():
    rows = [(ERA_LABELS[i], {c: s[i]['reg'].get(c, 0) for c in REG_CATS}) for i in range(8)]
    return stacked_chart(rows, REG_CATS, "Africa went from absent to half of the Council's work",
                         'Share of resolutions by region of the situation in the title, by era (institutional = admissions, elections, appointments)')

def inside_chart():
    ser = [dict(name='Human rights', values=[s[i]['themes']['human-rights'] for i in range(8)], color=GREY),
           dict(name='Children', values=[s[i]['themes']['children'] for i in range(8)], color=GREY, dash='5 3'),
           dict(name='Protection of civilians', values=[s[i]['themes']['civilians'] for i in range(8)], color=GREY, dash='2 3'),
           dict(name='Women', values=[s[i]['themes']['women'] for i in range(8)], color=BLUE, width=2.6, bold=True),
           dict(name='Sexual violence', values=[s[i]['themes']['sexual-violence'] for i in range(8)], color=ORANGE, width=2.2, bold=True)]
    return era_lines_chart(ERA_LABELS, ser, 'Civilians, women and children entered the texts after 1999',
                           'Share of resolutions whose text mentions each subject, by era')

def binding_chart():
    ser = [dict(name='"Decides"', values=[s[i]['flags']['decides'] for i in range(8)], color=BLUE, width=2.6, bold=True),
           dict(name='"Acting under Chapter VII"', values=[s[i]['flags']['ch7'] for i in range(8)], color=GREY, width=2.2, dash='5 3'),
           dict(name='"All necessary means/measures"', values=[s[i]['flags']['all_necessary'] for i in range(8)], color=GREY)]
    return era_lines_chart(ERA_LABELS, ser, 'The Council moved from recommending to deciding', 'Share of resolutions using binding or enforcement wording, by era')

def bare(svg):
    m = re.match(r'<svg viewBox="0 0 (\d+) (\d+)"', svg)
    w, h = int(m.group(1)), int(m.group(2))
    svg = re.sub(r'(</title>)<text[^>]*>.*?</text><text[^>]*>.*?</text>', r'\1', svg, count=1)
    return svg.replace(f'viewBox="0 0 {w} {h}"', f'viewBox="0 52 {w} {h-52}"', 1)

def fig(svg, cap):
    return f'<figure tabindex="0" aria-label="Chart">{svg}<figcaption>{cap}</figcaption></figure>'

CAP_VOTES = f'Source: UNSC votes since 1946 database, Sciences Po Atelier de cartographie and GRAM (CC BY 4.0), 1946 to {LAST_FULL}.'
CAP_TEXT = f'Source: full text of all {fmt(len(R))} resolutions (CR-UNSC corpus and UN machine-readable resolutions). Term counts are pattern matches, checked by hand on samples.'
CAP_TITLES = 'Source: resolution titles, classified by the region of the situation they concern.'

# ------------- themes (the six findings) -------------
THEME_PAGES = [
    ('from-advising-to-ordering', 'The Council went from recommending to ordering',
     f'"Decides" appears in {s[0]["flags"]["decides"]}% of resolutions in the founding era and {s[7]["flags"]["decides"]}% since 2022. "Acting under Chapter VII" went from about 1% of resolutions before 1988 to {s[7]["flags"]["ch7"]}%.'),
    ('language-of-threat', 'The vocabulary of war changed',
     f'"Aggression" peaked in 1975 to 1987, mostly about South Africa, then all but disappeared. "Breach of the peace" was found for only four wars, the last in 1990. "Threat to the peace" became the routine trigger: {s[0]["flags"]["threat"]}% of resolutions in the founding era, {s[7]["flags"]["threat"]}% today.'),
    ('the-veto', 'The veto map flipped twice',
     f'The USSR cast most vetoes until 1960, the United States from the 1970s to the 1990s, Russia and China since 2011. {TOTAL_VETOED} drafts have been vetoed since 1946.'),
    ('unity-and-division', 'Unity rose and is now falling',
     f'Unanimous adoption climbed from {s[0]["unan"]}% in the founding years to {s[5]["unan"]}% in 2001 to 2010, then fell to {Y[LAST_FULL]["u"]}% in {LAST_FULL}. On contested votes the US and Russia now agree {AGREE["US and Russia"][7]}% of the time, against {AGREE["US and Russia"][3]}% around 1990.'),
    ('wars-inside-states', 'From wars between states to wars inside them',
     f'Civilians, women, children and sexual violence were almost absent before 1999. Women now appear in {s[6]["themes"]["women"]}% of resolutions and civilians in {s[6]["themes"]["civilians"]}%. The median resolution grew from {s[1]["words"]} words in 1960 to 1974 to {fmt(s[6]["words"])} in 2011 to 2021.'),
    ('where-the-council-looks', 'Africa took over the agenda',
     f'Africa went from {s[0]["reg"].get("Africa",0)}% of resolutions in the founding era to {s[6]["reg"].get("Africa",0)}% in 2011 to 2021.'),
]

def theme_body(slug):
    if slug == 'from-advising-to-ordering':
        firsts = f'The first resolution to state "Acting under Chapter VII" is {rlink(253)}, on Southern Rhodesia. The phrase then stays rare until Iraq\'s invasion of Kuwait: from 1990 it becomes standard wording.'
        yr = [(str(y), Y[y]['ch7']) for y in FULL_YEARS if y >= 1985]
        return (fig(binding_chart(), CAP_TEXT) + f'<p>Before the 1990s most resolutions "call upon" or "request". The Council\'s binding power under Article 25 of the Charter was there, but rarely used. {firsts}</p>'
                + fig(bars_chart(yr, 'Chapter VII became standard wording after 1990', 'Share of resolutions each year that state "Acting under Chapter VII", 1985 onwards', accent_keys=('1990',), unit='%'), CAP_TEXT)
                + '<h2>Rules for every state</h2><p>Since 2001 some resolutions bind all UN members in general terms rather than about one crisis, which lawyers call the Council\'s quasi-legislative role. Three landmarks:</p><ul>'
                + f'<li>{rlink(1373)}: duties on all states to counter terrorist financing and safe havens.</li><li>{rlink(1540)}: all states must stop non-state actors getting weapons of mass destruction.</li><li>{rlink(2178)}: obligations on all states over foreign terrorist fighters.</li></ul>')
    if slug == 'language-of-threat':
        ag = ''.join(f'<li>{rlink(r["n"])} {e(r["topic"])}</li>' for r in AGG)
        br = ''.join(f'<li>{rlink(r["n"])} {e(r["topic"])}</li>' for r in BREACH)
        tg = ', '.join(f'{k} {v}' for k, v in AGG_TARGETS.most_common())
        after = ''.join(f'{rlink(r["n"])}' for r in AGG_AFTER_88)
        return (f'<p>Article 39 of the Charter lets the Council act once it finds a "threat to the peace, breach of the peace, or act of aggression". The three terms have had very different lives in the documents.</p>'
                + fig(lang_chart(), CAP_TEXT)
                + f'<h2>Aggression: a Cold War word</h2><p>{len(AGG)} resolutions speak of an "act of aggression". The states named in them: {tg}. After 1988 the phrase appears only once, in {after}, about hypothetical nuclear attacks. No adopted resolution has found an act of aggression since, including over Kuwait in 1990 and Ukraine since 2022. Resolution {rlink(2774)} speaks of the "Russian Federation-Ukraine conflict".</p><ul class="cols">{ag}</ul>'
                + f'<h2>Breach of the peace: open invasions only</h2><p>The Council has found a breach of the peace in only {len(BREACH)} resolutions, about four wars between states.</p><ul class="plain">{br}</ul>'
                + f'<h2>Threat to the peace: the all-purpose key</h2><p>The first finding is Palestine in 1948 ({rlink(54)}). Since 2001 the Council has also applied it to terrorism ({rlink(1373)}), weapons of mass destruction ({rlink(1540)}) and Ebola ({rlink(2177)}). It now appears in {s[7]["flags"]["threat"]}% of resolutions, because a threat finding is what opens Chapter VII.</p>'
                + '<p><a href="/language/?q=aggression">Track any word yourself in the Language lab</a>.</p>')
    if slug == 'the-veto':
        tot = ' '.join(f'{P5NAME[k]} {VETO_TOTAL[k]},' for k in P5KEYS).rstrip(',')
        rows = ''.join(f'<tr><td class="num">{d["date"]}</td><td>{e(d["symbol"])}</td><td>{e(d["title"][:140])}</td><td>{e(", ".join(d["vetoed_by"]))}</td><td class="num">{d["yes"]}-{d["no"]}-{d["abst"]}</td></tr>' for d in sorted([d for d in DRAFTS if d['outcome'] == 'vetoed'], key=lambda d: d['date'], reverse=True))
        joint = sorted([d for d in DRAFTS if d['outcome'] == 'vetoed' and d['votes'].get('RUSSIAN FEDERATION/USSR') == 'N' and d['votes'].get('CHINA') == 'N' and d['year'] > 1971], key=lambda d: d['date'], reverse=True)
        jrows = ''.join(f'<tr><td class="num">{d["date"]}</td><td>{e(d["symbol"])}</td><td>{e(d["title"][:140])}</td><td class="num">{d["yes"]}-{d["no"]}-{d["abst"]}</td></tr>' for d in joint)
        explain = (f'<h2>What is veto power?</h2><p>Decisions of the Security Council on anything beyond procedure need nine of the fifteen votes, and none of the five permanent members may vote against (Article 27 of the UN Charter). A single no vote from a permanent member therefore blocks a draft, however many members support it. That no vote is the veto. By long practice an abstention by a permanent member does not block adoption.</p>'
                   '<h2>Which countries have veto power?</h2><p>The five permanent members: China, France, Russia (the Soviet Union until December 1991), the United Kingdom and the United States. China\'s seat was held by the Republic of China (Taipei) until October 1971. The ten elected members have no veto.</p>')
        joint_html = f'<h2>Joint Russia and China vetoes</h2><p>{len(joint)} drafts were vetoed by Russia and China voting no together, all since 1972, newest first.</p><div class="tw" tabindex="0" role="region" aria-label="Table"><table><thead><tr><th>Date</th><th>Document</th><th>Subject</th><th class="num">Vote</th></tr></thead><tbody>{jrows}</tbody></table></div>'
        return (explain + fig(veto_chart(), CAP_VOTES + ' A draft vetoed by two members counts for both.') + joint_html
                + f'<p>Totals since 1946, counting each member\'s no votes on vetoed drafts: {tot}. The US cast its first veto in {first_us_veto}.</p>'
                + f'<h2>Every vetoed draft</h2><p class="meta">{TOTAL_VETOED} vetoed drafts, newest first. Votes are yes-no-abstain. <a href="/votes/drafts/">All {len(DRAFTS)} failed and vetoed drafts</a>.</p><div class="tw" tabindex="0" role="region" aria-label="Table"><table><thead><tr><th>Date</th><th>Document</th><th>Subject</th><th>Vetoed by</th><th class="num">Vote</th></tr></thead><tbody>{rows}</tbody></table></div>')
    if slug == 'unity-and-division':
        ab = ''.join(f'<tr><td>{ERA_LABELS[i]}</td>' + ''.join(f'<td class="num">{s[i]["absP5"][k]}</td>' for k in P5KEYS) + '</tr>' for i in range(8))
        return (fig(timeline('Unanimity rose to over 90% after the Cold War and is now falling'), CAP_VOTES)
                + fig(agree_chart(), CAP_VOTES + f' {fmt(CONTESTED_N)} contested votes.')
                + f'<h2>Abstention is the new protest</h2><p>Permanent members rarely veto adopted texts; they abstain. Abstentions by each permanent member on adopted resolutions:</p><div class="tw" tabindex="0" role="region" aria-label="Table"><table><thead><tr><th>Era</th>' + ''.join(f'<th class="num">{P5NAME[k]}</th>' for k in P5KEYS) + f'</tr></thead><tbody>{ab}</tbody></table></div><p><a href="/votes/">See every member\'s voting record</a>.</p>')
    if slug == 'wars-inside-states':
        return (fig(inside_chart(), CAP_TEXT)
                + fig(bars_chart([(ERA_LABELS[i], s[i]['words']) for i in range(8)], 'Resolutions grew several times longer', 'Median number of words per resolution, by era', accent_keys=(ERA_LABELS[6],)), CAP_TEXT)
                + f'<p>The growth in length reflects multidimensional mandates: a peace operation resolution now lists tasks on civilians, human rights, elections, sexual violence, children and the rule of law. <a href="/themes/new-agendas/">When each new agenda arrived</a>.</p>')
    if slug == 'where-the-council-looks':
        cc = collections.Counter(c for r in R for c in r['countries'])
        top = [(c, v, '') for c, v in cc.most_common(20)]
        return (fig(region_chart(), CAP_TITLES) + fig(hbars_chart(top, 'The 20 countries most often the subject of a resolution', 'Number of resolutions tagged with each country, 1946 to 2026', accent=3), 'Source: country tags of the CR-UNSC corpus (from the UN Digital Library); resolutions after January 2026 not tagged.')
                + '<p>The map of crises moved with history: Asia and Palestine in the founding years, decolonisation and Cyprus in the 1960s, the Middle East and Southern Africa in the late Cold War, the Balkans in the 1990s, then Africa\'s civil wars. Europe has almost left the adopted texts, partly because of the veto: Ukraine appears in the vetoed drafts.</p>')

AGENDAS = [(2018, 2417, 'Starvation of civilians as a method of warfare', r'food insecurity|starvation of civilians'), (2015, 2250, 'Youth, peace and security', r'youth, peace|youth and peace'),
           (2015, 2242, 'Climate change, inside a women and peace resolution', r'climate change'), (2014, 2177, 'Ebola declared a threat to international peace and security', r'\bhiv\b|ebola|covid'),
           (2014, 2178, 'Foreign terrorist fighters, with duties on all states', r'foreign terrorist fighters'), (2008, 1816, 'Piracy off Somalia', r'\bpiracy\b'),
           (2008, 1820, 'Sexual violence as a tactic of war', r'sexual violence'), (2006, 1674, 'Responsibility to protect, citing the 2005 World Summit', r'responsibility to protect'),
           (2004, 1540, 'Weapons of mass destruction and non-state actors', None), (2001, 1373, 'Terrorism as a general threat, with duties on all states', r'terroris'),
           (2000, 1325, 'Women and peace and security', r'women and peace|women, peace'), (2000, 1308, 'HIV/AIDS as a security issue', None),
           (1999, 1265, 'Protection of civilians', r'protection of civilians'), (1999, 1261, 'Children and armed conflict', r'children (and|in) armed conflict|child soldier'),
           (1990, 678, '"All necessary means": authorising force', r'all necessary means'), (1968, 253, 'First "Acting under Chapter VII"', r'(acting|action) under chapter v[il1]{2}\b'),
           (1966, 232, 'First mandatory sanctions (Southern Rhodesia)', None), (1964, 186, '"Peace-keeping" (the Cyprus force)', r'peace-?keep'),
           (1948, 54, 'First "threat to the peace" finding (Palestine)', r'threat to (international )?(the )?peace')]
def agendas_body():
    rows = ''
    for y, n, lab, p in AGENDAS:
        cnt = sum(1 for r in R if re.search(p, r['text'].lower())) if p else ''
        rows += f'<tr><td class="num">{y}</td><td>{rlink(n)}</td><td>{e(lab)}</td><td class="num">{cnt}</td></tr>'
    return ('<p>Almost every theme the Council now treats as routine arrived after 1990, most between 1999 and 2018. Each row is the landmark resolution where the idea is set out as Council business. The last column counts resolutions whose text uses the term.</p>'
            + f'<div class="tw" tabindex="0" role="region" aria-label="Table"><table><thead><tr><th class="num">Year</th><th>Resolution</th><th>What entered the vocabulary</th><th class="num">Resolutions using it</th></tr></thead><tbody>{rows}</tbody></table></div>'
            + '<p>The Council started as a body that refereed wars between states. It is now a body that legislates on how wars are fought inside states, and on threats that are not wars at all.</p>')

# ------------- HOME -------------
def home():
    stats = f'''<div class="stats"><div><b>{fmt(len(R))}</b><span>resolutions, 1946 to 2026</span></div><div><b>{TOTAL_VETOED}</b><span>vetoed drafts</span></div><div><b>{len(COUNTRIES)}</b><span>countries that have sat on the Council</span></div><div><b>{fmt(len(allvotes))}</b><span>recorded votes</span></div></div>'''
    finds = ''.join(f'<li><b>{e(t)}.</b> {e(x)} <a class="more" href="/themes/{sl}/">Read more</a></li>' for sl, t, x in THEME_PAGES)
    glance = f'The Council adopted about {s[0]["per_year"]} resolutions a year in its first era and over 60 a year from 1994 to 2010. Output has fallen every year since 2021, to {Y[LAST_FULL]["n"]} in {LAST_FULL}, the lowest since {lowest_since}. The quiet years of the Cold War were divided years: unanimity often sat below half.'
    maxn = max(Y[y]['n'] for y in FULL_YEARS); bw = 560 / len(FULL_YEARS)
    mini = ''.join(f'<rect x="{i*bw+0.6:.1f}" y="{240-Y[y]["n"]/maxn*240:.1f}" width="{bw-1.2:.1f}" height="{Y[y]["n"]/maxn*240:.1f}" fill="{BLUE if y in (peak_y, LAST_FULL) else GREY}"><title>{y}: {Y[y]["n"]} resolutions</title></rect>' for i, y in enumerate(FULL_YEARS))
    charts = [binding_chart(), lang_chart(), veto_chart(), agree_chart(), inside_chart(), region_chart()]
    blocks = '<h2>What stands out</h2><div class="blocks">' + ''.join(
        f'<a class="block" href="/themes/{sl}/"><div class="btext"><span class="no{" o" if i == 1 else ""}">{i+1:02d}</span><b>{e(t)}</b><p>{e(x)}</p><span class="more">Read the full analysis</span></div><div class="bchart" role="img" aria-label="Chart: {e(t)}">{bare(charts[i])}</div></a>'
        for i, (sl, t, x) in enumerate(THEME_PAGES)) + '</div>'
    basics = f'''<h2>New to the Security Council?</h2><p class="muted">The basics in five boxes. <a href="/about/security-council/">Read the full explainer</a>.</p>
<div class="basics">
<a class="basic" href="/about/security-council/"><span class="tag">What it is</span><b>The UN's body for peace and security</b><span>All UN members agree to carry out its decisions (Article 25 of the Charter).</span></a>
<a class="basic" href="/votes/"><span class="tag">Who sits on it</span><b>15 members, 5 permanent</b><span>China, France, Russia, the United Kingdom and the United States, plus ten members elected for two years.</span></a>
<a class="basic" href="/themes/the-veto/"><span class="tag">How it decides</span><b>Nine votes and no veto</b><span>A single no from a permanent member blocks a draft. {TOTAL_VETOED} drafts have been vetoed since 1946.</span></a>
<a class="basic" href="/themes/from-advising-to-ordering/"><span class="tag">What it can do</span><b>Recommend, or order</b><span>Chapter VI to settle disputes; Chapter VII for sanctions, peace operations and the use of force.</span></a>
<a class="basic" href="/resolutions/"><span class="tag">What a resolution is</span><b>{fmt(len(R))} decisions, numbered since 1946</b><span>Browse every resolution with its full text, vote and citations.</span></a>
</div>'''
    body = f'''<section class="hero"><div><p class="kicker">An independent record</p><h1>80 years of the UN Security Council</h1>
<p class="lede">Every UN Security Council resolution, vote and veto since 1946, and what they show about war, power and the Council itself. Every figure on this site is counted from the documents.</p>
<form class="search-hero" action="/search/" role="search"><label for="hq" class="sr">Search all resolutions</label><input id="hq" name="q" type="search" placeholder="Search all {fmt(len(R))} resolutions: Rwanda, sanctions, 242"><button>Search</button></form>
<div class="chips"><a class="chip" href="/resolutions/242/">Resolution 242</a><a class="chip" href="/resolutions/1325/">1325 Women and peace</a><a class="chip" href="/resolutions/678/">678 Kuwait</a><a class="chip" href="/themes/the-veto/">Every veto</a></div></div>
<div class="mini"><p class="meta" style="font-weight:700;color:var(--text);margin-bottom:6px">Resolutions per year, {FULL_YEARS[0]} to {LAST_FULL}</p><svg viewBox="0 0 560 240" role="img" aria-label="Resolutions per year, {FULL_YEARS[0]} to {LAST_FULL}: {Y[peak_y]['n']} in {peak_y}, {Y[LAST_FULL]['n']} in {LAST_FULL}">{mini}</svg><div class="lbl"><span>{FULL_YEARS[0]}</span><b>{Y[peak_y]['n']} in {peak_y}</b><b>{Y[LAST_FULL]['n']} in {LAST_FULL}</b></div></div></section>
{stats}
{blocks}
<h2>At a glance</h2>{fig(timeline(), CAP_VOTES)}<p>{glance}</p>
<h2>The eight eras</h2><p>The periods follow political breaks, not decades. Each break shows in the data: a jump in output, a change in unanimity, a new veto caster or new words.</p>{era_table()}
{basics}
<h2>Explore</h2><div class="cards"><a class="card" href="/language/"><b>Language lab</b><span>Track any word or phrase through 80 years of resolutions.</span></a><a class="card" href="/votes/"><b>Members and votes</b><span>Every member's record: abstentions, no votes and vetoes.</span></a><a class="card" href="/themes/new-agendas/"><b>New agendas</b><span>When civilians, women, terrorism, climate and others arrived.</span></a></div>'''
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', '@id': SITE + '/#website', 'name': NAME, 'url': SITE + '/', 'publisher': {'@id': SITE + '/#org'},
         'potentialAction': {'@type': 'SearchAction', 'target': SITE + '/search/?q={q}', 'query-input': 'required name=q'}},
        {'@type': 'Organization', '@id': SITE + '/#org', 'name': NAME, 'url': SITE + '/', 'logo': {'@type': 'ImageObject', 'url': SITE + '/assets/logo.png', 'width': 512, 'height': 512},
         'founder': {'@type': 'Person', 'name': "Daniel D'Esposito", 'sameAs': 'https://www.linkedin.com/in/ddesposito'}}]}
    write('/', page('/', 'Every UN Security Council resolution, vote and veto since 1946', f'An independent record of all {fmt(len(R))} UN Security Council resolutions, votes and vetoes since 1946, with eras, themes, full text and search.', body, jsonld=ld))

# ------------- ERAS -------------
def eras_pages():
    body = f'<h1>The eight eras of the Security Council</h1><p class="lede">Eighty years of resolutions, split at the political breaks that changed how the Council worked.</p>{fig(timeline(), CAP_VOTES)}{era_table()}'
    write('/eras/', page('/eras/', 'The eight eras of the UN Security Council', 'From the founding years to Ukraine: how output, unity, vetoes and language changed in each era of the UN Security Council.', body, wide=True))
    for i, er in enumerate(ERAS):
        st = s[i]
        yrs = [y for y in st['years'] if y in Y]
        prev = s[i - 1] if i else None
        rose = []
        if prev:
            for k, lab in THEMES.items():
                d = st['themes'][k] - prev['themes'][k]
                if d >= 5:
                    rose.append((d, lab, st['themes'][k], prev['themes'][k]))
            rose.sort(reverse=True)
        rose_html = ''.join(f'<li>{e(lab)}: {b}% to {a}%</li>' for d, lab, a, b in rose[:6]) or '<li>No subject rose by 5 points or more.</li>'
        veto = ', '.join(f'{P5NAME[k]} {st["vetoN"][k]}' for k in P5KEYS if st['vetoN'][k]) or 'none'
        top = ''.join(f'<li>{rlink(r["n"])} {e(r["topic"])} <span class="meta">cited by {len(r["cited_by"])} later resolutions</span></li>' for r in st['top'])
        reg = ''.join(f'<tr><td>{c}</td><td class="num">{st["reg"].get(c,0)}%</td></tr>' for c in REG_CATS)
        lst = ''.join(f'<li>{rlink(r["n"])} {e(r["topic"][:110])}</li>' for r in R if r['era'] == i)
        nav = (f'<p class="meta">{"Previous: " + era_link(i-1) if i else ""}{" &middot; " if 0 < i < 7 else ""}{"Next: " + era_link(i+1) if i < 7 else ""}</p>')
        body = f'''<p class="kicker">Era {i+1} of 8</p><h1>{er["a"]} to {er["b"]}: {e(er["name"])}</h1><p class="lede">Opened by: {e(OPENED[i])}.</p>
<p>{ERA_NOTES[i]}</p>
<div class="stats"><div><b>{st["n"]}</b><span>resolutions</span></div><div><b>{st["per_year"]}</b><span>per year</span></div><div><b>{st["unan"]}%</b><span>adopted unanimously</span></div><div><b>{st["vetoed"]}</b><span>vetoed drafts</span></div><div><b>{st["flags"]["ch7"]}%</b><span>under Chapter VII</span></div></div>
{fig(bars_chart([(str(y), Y[y]['n']) for y in yrs], f'Resolutions per year, {er["a"]} to {er["b"]}', 'Resolutions adopted each year', accent_keys=(str(max(yrs, key=lambda y: Y[y]['n'])),)), CAP_VOTES)}
<h2>Where the Council looked</h2><div class="tw" tabindex="0" role="region" aria-label="Table"><table><thead><tr><th>Region of the situation</th><th class="num">Share</th></tr></thead><tbody>{reg}</tbody></table></div>
<h2>What rose in the texts</h2><p>Subjects whose share of resolutions grew by 5 points or more on the previous era.</p><ul>{rose_html}</ul>
<h2>Vetoes</h2><p>{st["vetoed"]} vetoed drafts. No votes by permanent members on them: {veto}. {st["failed"]} further drafts failed for lack of votes.</p>
<h2>Most cited resolutions of the era</h2><ul class="plain">{top}</ul>
<h2>All {st["n"]} resolutions</h2><ul class="cols">{lst}</ul>{nav}'''
        write(f'/eras/{er["slug"]}/', page(f'/eras/{er["slug"]}/', f'{er["a"]} to {er["b"]}: {er["name"]}', f'The UN Security Council in {er["a"]} to {er["b"]}: {st["n"]} resolutions, {st["unan"]}% unanimous, {st["vetoed"]} vetoed drafts, key resolutions and changes in language.',
                                                     body, pagefind=True, filters={'type': 'Analysis'}, crumbs=[('/', 'Home'), ('/eras/', 'Eras'), (None, er['name'])]))

# ------------- THEMES -------------
def theme_pages():
    cards = ''.join(f'<a class="card" href="/themes/{sl}/"><b>{e(t)}</b><span>{e(x)}</span></a>' for sl, t, x in THEME_PAGES)
    cards += '<a class="card" href="/themes/new-agendas/"><b>New agendas and tools</b><span>When each theme now treated as routine first entered the texts.</span></a>'
    write('/themes/', page('/themes/', 'Themes: what 80 years of Security Council resolutions show', 'Six findings from every UN Security Council resolution since 1946: binding power, the language of threat, the veto, unity, wars inside states and Africa.', f'<h1>What the documents show</h1><p class="lede">Six findings, each measured across all {fmt(len(R))} resolutions and every recorded vote.</p><div class="cards">{cards}</div>'))
    SEO_TITLE = {'the-veto': 'UN Security Council veto power: every veto since 1946', 'language-of-threat': 'Threat to the peace, breach of the peace, aggression: the Security Council\'s words',
                 'unity-and-division': 'How the UN Security Council votes: unanimity and division since 1946', 'where-the-council-looks': 'Which countries the UN Security Council deals with most',
                 'from-advising-to-ordering': 'Chapter VII and binding Security Council resolutions', 'wars-inside-states': 'Civilians, women and children in Security Council resolutions'}
    for sl, t, x in THEME_PAGES:
        body = f'<p class="kicker">Theme</p><h1>{e(t)}</h1><p class="lede">{e(x)}</p>{theme_body(sl)}'
        write(f'/themes/{sl}/', page(f'/themes/{sl}/', SEO_TITLE.get(sl, t), x, body, pagefind=True, filters={'type': 'Analysis'}, crumbs=[('/', 'Home'), ('/themes/', 'Themes'), (None, t)]))
    write('/themes/new-agendas/', page('/themes/new-agendas/', 'New agendas and tools of the Security Council', 'When protection of civilians, women and peace, terrorism, climate change and other agendas first entered UN Security Council resolutions.',
                                        f'<p class="kicker">Theme</p><h1>New agendas and tools</h1>{agendas_body()}', pagefind=True, filters={'type': 'Analysis'}, crumbs=[('/', 'Home'), ('/themes/', 'Themes'), (None, 'New agendas')]))

# ------------- VOTES & COUNTRIES -------------
def ranges(ys):
    out = []
    for y in ys:
        if out and y == out[-1][1] + 1:
            out[-1][1] = y
        else:
            out.append([y, y])
    return ', '.join(f'{a}' if a == b else f'{a} to {b}' for a, b in out)

def about_html(c):
    nm = c['name'].lower().replace('russia / ussr', 'russian federation')
    rs = [r for r in R if any(c.lower() == nm or c.lower().startswith(nm.split(' /')[0]) for c in r['countries'])]
    if not rs:
        return ''
    lst = ''.join(f'<li>{rlink(r["n"])} {e(r["topic"][:110])}</li>' for r in rs)
    return f'<h2>Resolutions about {e(c["name"])}</h2><p>{len(rs)} resolutions are tagged with {e(c["name"])} as the country concerned.</p><details><summary>Show all {len(rs)}</summary><ul class="cols">{lst}</ul></details>'

def votes_pages():
    rows = ''
    for c in sorted(COUNTRIES, key=lambda c: c['name']):
        k = c['counts']
        abst = k.get('adopted|A', 0); no = k.get('adopted|N', 0) + k.get('lack of maj.|N', 0); veto = k.get('vetoed|N', 0) if c['p5'] else 0
        rows += f'<tr><td><a href="/votes/{c["slug"]}/">{e(c["name"])}</a>{" (permanent)" if c["p5"] else ""}</td><td class="num">{len(c["years"])}</td><td class="num">{abst}</td><td class="num">{no}</td><td class="num">{veto if c["p5"] else ""}</td></tr>'
    curnames = [CNAME_ANY(c) for c in D['current_members']]
    p5 = [x for x in curnames if x[1]]; e10 = [x for x in curnames if not x[1]]
    li = lambda xs: ', '.join(f'<a href="/votes/{s}/">{e(nm)}</a>' if s else e(nm) for nm, _, s in xs)
    body = f'''<h1>UN Security Council members and votes</h1><p class="lede">How each of the {len(COUNTRIES)} countries that have sat on the Council voted, from {FULL_YEARS[0]} to {LAST_FULL}.</p>
<h2>Members in 2026</h2><p>The Council has fifteen members. <b>Permanent members</b> (with veto power): {li(p5)}. <b>Elected members</b>, chosen by the General Assembly for two-year terms: {li(e10)}. <span class="meta">Members voting on {D["current_as_of"]}.</span></p>
{fig(agree_chart(), CAP_VOTES)}<p><a href="/themes/the-veto/">Every veto</a> &middot; <a href="/votes/drafts/">All failed and vetoed drafts</a> &middot; <a href="/themes/unity-and-division/">Unity and division</a></p>
<h2>All members</h2><p class="meta">Years with at least one recorded vote. Abstentions on adopted resolutions; no votes on adopted and failed drafts; vetoes are no votes by a permanent member on a vetoed draft.</p>
<div class="tw" tabindex="0" role="region" aria-label="Table"><table><thead><tr><th>Country</th><th class="num">Years</th><th class="num">Abstentions</th><th class="num">No votes</th><th class="num">Vetoes</th></tr></thead><tbody>{rows}</tbody></table></div>'''
    write('/votes/', page('/votes/', 'UN Security Council members: permanent, elected and how they voted since 1946', f'Voting records of all {len(COUNTRIES)} countries that have sat on the UN Security Council: abstentions, no votes and vetoes since 1946.', body, wide=True))
    # drafts
    dr = ''.join(f'<tr><td class="num">{d["date"]}</td><td>{e(d["symbol"])}</td><td>{e(d["title"][:150])}</td><td>{"Vetoed by " + e(", ".join(d["vetoed_by"])) if d["outcome"] == "vetoed" else "Not enough votes"}</td><td class="num">{d["yes"]}-{d["no"]}-{d["abst"]}</td></tr>' for d in sorted(DRAFTS, key=lambda d: d['date'], reverse=True))
    write('/votes/drafts/', page('/votes/drafts/', 'Every failed and vetoed Security Council draft since 1946', f'All {len(DRAFTS)} UN Security Council drafts that were vetoed ({TOTAL_VETOED}) or failed for lack of votes ({TOTAL_FAILED}) since 1946.',
                                 f'<h1>Failed and vetoed drafts</h1><p class="lede">{len(DRAFTS)} drafts put to the vote and not adopted since 1946: {TOTAL_VETOED} vetoed, {TOTAL_FAILED} without enough votes.</p><div class="tw" tabindex="0" role="region" aria-label="Table"><table><thead><tr><th>Date</th><th>Document</th><th>Subject</th><th>Outcome</th><th class="num">Vote</th></tr></thead><tbody>{dr}</tbody></table></div>', wide=True, crumbs=[('/', 'Home'), ('/votes/', 'Votes'), (None, 'Drafts')]))
    for c in COUNTRIES:
        key = c['key']
        notyes = [(r, r['member_votes'][key]) for r in R if r['member_votes'].get(key) in ('A', 'N', 'NV')]
        dvotes = [(d, d['votes'][key]) for d in DRAFTS if key in d['votes']]
        k = c['counts']
        yes = k.get('adopted|Y', 0)
        li = ''.join(f'<li>{rlink(r["n"])} {e(r["topic"][:100])} <span class="badge grey">{ {"A": "abstained", "N": "voted no", "NV": "did not vote"}[v] }</span></li>' for r, v in notyes)
        dl = ''.join(f'<li>{d["date"]} {e(d["symbol"])} {e(d["title"][:90])} <span class="badge {"orange" if d["outcome"] == "vetoed" and v == "N" and c["p5"] else "grey"}">{ {"Y": "yes", "N": "no", "A": "abstained", "NV": "did not vote", "?": "unknown"}.get(v, v) }</span></li>' for d, v in sorted(dvotes, key=lambda t: t[0]['date'], reverse=True))
        body = f'''<h1>{e(c["name"])} on the Security Council</h1><p class="lede">{"Permanent member. " if c["p5"] else ""}Years with recorded votes: {ranges(c["years"])}.</p>
<div class="stats"><div><b>{len(c["years"])}</b><span>years with votes</span></div><div><b>{yes}</b><span>yes votes on adopted resolutions</span></div><div><b>{k.get("adopted|A",0)}</b><span>abstentions on adopted resolutions</span></div><div><b>{sum(1 for d,v in dvotes if v=="N")}</b><span>no votes on failed or vetoed drafts</span></div></div>
{about_html(c)}<h2>Adopted resolutions where {e(c["name"])} did not vote yes</h2>{"<ul class=plain>" + li + "</ul>" if li else "<p>None: every recorded vote on an adopted resolution was yes.</p>"}
<h2>Votes on failed and vetoed drafts</h2>{"<ul class=plain>" + dl + "</ul>" if dl else "<p>None recorded.</p>"}'''
        write(f'/votes/{c["slug"]}/', page(f'/votes/{c["slug"]}/', f'{c["name"]}: UN Security Council voting record', f'How {c["name"]} voted on the UN Security Council: years served, abstentions, no votes{" and vetoes" if c["p5"] else ""}, resolution by resolution.',
                                           body, pagefind=True, filters={'type': 'Country'}, crumbs=[('/', 'Home'), ('/votes/', 'Votes'), (None, c['name'])]))

# ------------- RESOLUTIONS -------------
CR_DIR = '/home/claude/crunsc/CR-UNSC_2026-08-19_EN_TXT_BEST'
CR_FILES = {int(re.search(r'S_RES_(\d+)_', os.path.basename(f)).group(1)): f for f in glob.glob(CR_DIR + '/*.txt')}
def paragraphs(n, flat):
    f = CR_FILES.get(n)
    if f:
        raw = open(f, errors='ignore').read()
        raw = re.sub(r'(\w)-\n(\w)', r'\1\2', raw)
        paras = [re.sub(r'\s+', ' ', p).strip() for p in re.split(r'\n\s*\n', raw)]
    else:
        paras = [flat]
    out = []
    for p in paras:
        out += [x.strip() for x in re.split(r'(?<=[;:.,])\s+(?=\d{1,2}\.\s+[A-Z])', p) if x.strip()]
    return out

GA_NOTE = {181: '<p class="note">Looking for General Assembly resolution 181 (1947) on the partition of Palestine? This is Security Council resolution 181 (1963). General Assembly resolutions are on the <a href="https://digitallibrary.un.org">UN Digital Library</a>.</p>',
           194: '<p class="note">Looking for General Assembly resolution 194 (1948) on Palestine refugees and the right of return? This is Security Council resolution 194 (1964). General Assembly resolutions are on the <a href="https://digitallibrary.un.org">UN Digital Library</a>.</p>'}
def CNAME_ANY(raw):
    key = {'RUSSIAN FEDERATION': 'RUSSIAN FEDERATION/USSR'}.get(raw, raw)
    for c in COUNTRIES:
        if c['key'] == key:
            return (c['name'], c['p5'], c['slug'])
    nm = ' '.join(w.capitalize() if w not in ('OF', 'THE', 'AND') else w.lower() for w in raw.split())
    return (nm, raw in ('CHINA', 'FRANCE', 'RUSSIAN FEDERATION', 'UNITED KINGDOM', 'UNITED STATES'), None)
VOTE_WORD = {'Y': 'Yes', 'N': 'No', 'A': 'Abstained', 'NV': 'Did not vote', '?': 'Unknown'}
CNAME = {c['key']: c for c in COUNTRIES}
def resolution_pages():
    for r in R:
        n = r['n']
        badges = ''
        if r['flags']['ch7']: badges += '<span class="badge">Chapter VII</span>'
        if r['flags']['threat']: badges += '<span class="badge">Threat to the peace</span>'
        if r['flags']['breach']: badges += '<span class="badge orange">Breach of the peace</span>'
        if r['flags']['act_aggression']: badges += '<span class="badge orange">Act of aggression</span>'
        badges += '<span class="badge grey">Unanimous</span>' if r['unanimous'] else ('<span class="badge grey">Not unanimous</span>' if r['unanimous'] is False else '')
        chips = ''.join(f'<a class="chip" href="/search/?theme={e(THEMES[t])}">{e(THEMES[t])}</a>' for t in r['themes'])
        mv = ''
        if r['member_votes']:
            cells = sorted(r['member_votes'].items(), key=lambda kv: (kv[1] == 'Y', CNAME.get(kv[0], {'name': kv[0]})['name']))
            mv = '<details><summary>How each member voted</summary><ul class="cols">' + ''.join(f'<li>{"<b>" if v != "Y" else ""}<a href="/votes/{CNAME[k]["slug"]}/">{e(CNAME[k]["name"])}</a>: {VOTE_WORD.get(v, v)}{"</b>" if v != "Y" else ""}</li>' for k, v in cells if k in CNAME) + '</ul></details>'
        cites = ', '.join(rlink(x) for x in r['cites'] if x in BYN)
        cited = ', '.join(rlink(x) for x in r['cited_by'][:60] if x in BYN)
        more = f' and {len(r["cited_by"]) - 60} more' if len(r['cited_by']) > 60 else ''
        text = ''.join(f'<p>{e(p)}</p>' for p in paragraphs(n, r['text']))
        ga = GA_NOTE.get(n, '')
        prev_n, next_n = (n - 1 if n > 1 else None), (n + 1 if n < len(R) else None)
        vote = f'<div class="vote"><span>Yes <b>{e(r["yes"])}</b></span><span>No <b>{e(r["no"])}</b></span><span>Abstained <b>{e(r["abst"])}</b></span>' + (f'<span>Did not vote <b>{e(r["nonvote"])}</b></span>' if r['nonvote'] not in ('', '0', '00', '000') else '') + '</div>'
        place = f' &middot; {e(", ".join(r["countries"]))}' if r['countries'] else ''
        body = f'''<p class="kicker" data-pagefind-ignore>{e(r["sym"])} &middot; {e(r["date"])}</p>
<h1 data-pagefind-meta="title">UN Security Council Resolution {n} ({r["year"]})</h1><p class="lede" data-pagefind-meta="topic">{e(r["topic"])}</p>
<div data-pagefind-ignore>{ga}<p class="meta">{era_link(r["era"])} &middot; {e(r["region"])}{place}</p>
<div>{badges}</div>{vote}{mv}
<div class="chips">{chips}</div>
<p class="meta"><a href="{e(r["url_en"])}">Official document (PDF)</a>{" &middot; Draft " + e(r["draft"]) if r["draft"] else ""}{" &middot; Meeting record " + e(r["meeting"]) if r["meeting"] else ""}</p>
{"<h2>Cites</h2><p>" + cites + "</p>" if cites else ""}{"<h2>Cited by later resolutions</h2><p>" + cited + more + "</p>" if cited else ""}</div>
<div class="text">{text}</div>
<p class="meta" data-pagefind-ignore>{"<a href=/resolutions/%d/>Previous: %d</a>" % (prev_n, prev_n) if prev_n else ""}{" &middot; " if prev_n and next_n else ""}{"<a href=/resolutions/%d/>Next: %d</a>" % (next_n, next_n) if next_n else ""} &middot; <a href="/resolutions/{r["year"]}/">All resolutions of {r["year"]}</a></p>'''
        filters = {'type': 'Resolution', 'era': ERA_LABELS[r['era']] + ' ' + ERAS[r['era']]['short'], 'year': str(r['year']), 'region': r['region'],
                   'vote': 'Unanimous' if r['unanimous'] else ('Not unanimous' if r['unanimous'] is False else 'Unknown'),
                   'theme': [THEMES[t] for t in r['themes']]}
        fnd = []
        if r['flags']['ch7']: fnd.append('Chapter VII')
        if r['flags']['threat']: fnd.append('Threat to the peace')
        if r['flags']['breach']: fnd.append('Breach of the peace')
        if r['flags']['act_aggression']: fnd.append('Act of aggression')
        if fnd: filters['charter'] = fnd
        if r['countries']: filters['country'] = r['countries']
        title = f'UN Security Council Resolution {n} ({r["year"]}): full text and vote'
        desc = f'Full text and vote of UN Security Council resolution {n} ({r["year"]}), adopted {r["date"]}: {r["topic"]}.'
        ld = {'@context': 'https://schema.org', '@type': 'Legislation', 'name': f'Security Council resolution {n} ({r["year"]})', 'legislationIdentifier': r['sym'], 'datePublished': r['date'],
              'about': r['topic'], 'legislationPassedBy': {'@type': 'Organization', 'name': 'United Nations Security Council'}, 'url': SITE + f'/resolutions/{n}/', 'sameAs': r['url_en']}
        write(f'/resolutions/{n}/', page(f'/resolutions/{n}/', title[:110], desc[:300], body, jsonld=ld, pagefind=True, filters=filters, crumbs=[('/', 'Home'), ('/resolutions/', 'Resolutions'), (f'/resolutions/{r["year"]}/', str(r['year'])), (None, str(n))]))
    # year pages and index
    yl = ''
    for y in years:
        rs = [r for r in R if r['year'] == y]
        lst = ''.join(f'<li>{rlink(r["n"])} {e(r["topic"])}</li>' for r in rs)
        write(f'/resolutions/{y}/', page(f'/resolutions/{y}/', f'UN Security Council resolutions of {y}', f'All {len(rs)} UN Security Council resolutions adopted in {y}, with full text and votes.',
                                         f'<h1>Resolutions of {y}</h1><p class="lede">{len(rs)} resolutions{f", {Y[y][chr(117)]}% unanimous" if Y[y]["u"] is not None else ""}. {era_link(rs[0]["era"])}.</p><ul class="plain">{lst}</ul>', crumbs=[('/', 'Home'), ('/resolutions/', 'Resolutions'), (None, str(y))]))
        yl += f'<a href="/resolutions/{y}/">{y}</a> <span class="meta">{len(rs)}</span> '
    write('/resolutions/', page('/resolutions/', 'All UN Security Council resolutions since 1946', f'Browse all {fmt(len(R))} UN Security Council resolutions by year, with full text, votes and citations.',
                                f'<h1>All resolutions</h1><p class="lede">{fmt(len(R))} resolutions, from resolution 1 on 25 January 1946 to resolution {len(R)} in {years[-1]}. Pick a year, or <a href="/search/">search the full text</a>.</p><div class="yearnav">{yl}</div>'))

# ------------- SEARCH, LAB, ABOUT -------------
def misc_pages():
    write('/search/', page('/search/', 'Search all Security Council resolutions', f'Full-text search with filters across all {fmt(len(R))} UN Security Council resolutions since 1946.',
                           f'''<h1>Super search</h1><p class="lede">Search the full text of every resolution. Narrow by era, region, theme, Charter wording and vote.</p>
<form class="search-hero" id="sform" role="search"><label for="q" class="sr">Search</label><input id="q" class="q" type="search" placeholder="Words or a phrase in quotes" autocomplete="off"><button>Search</button></form>
<div class="sgrid"><aside class="facets" id="facets" aria-label="Filters"></aside><div><div class="count" id="count" aria-live="polite"></div><div class="results" id="results"></div><p><button class="btn light" id="more" hidden>More results</button></p></div></div>
<script src="/assets/search.js" type="module"></script>''', wide=True, index=True))
    presets = ['aggression', 'breach of the peace', 'threat to the peace', 'Chapter VII', 'sovereignty', 'self-determination', 'terrorism', 'climate change', 'sexual violence', 'apartheid', 'humanitarian', 'all necessary means']
    chips = ''.join(f'<button type="button" class="chip" data-q="{e(p)}">{e(p)}</button>' for p in presets)
    write('/language/', page('/language/', 'Language lab: how the Security Council\'s words changed', 'Type any word or phrase and see how often UN Security Council resolutions used it, year by year since 1946.',
                             f'''<h1>Language lab</h1><p class="lede">Type a word or a phrase and see the share of resolutions using it each year since 1946.</p>
<form class="search-hero" id="lform"><label for="lq" class="sr">Word or phrase</label><input id="lq" class="q" type="search" placeholder="e.g. aggression" autocomplete="off"><button>Show</button></form>
<div class="chips">{chips}</div>
<figure id="lchart" aria-live="polite"></figure><div id="llist"></div>
<p class="note">How it works: the lab counts resolutions whose text matches the word (and related forms, so "sanction" also finds "sanctions"). Put a phrase in quotes for an exact match. Shares are of all resolutions adopted that year.</p>
<script src="/assets/lab.js" type="module"></script>'''))
    about = f'''<h1>About this record</h1>
<p class="lede">{NAME} is an independent, non-commercial overlay on the public documentation of the United Nations Security Council. It is not affiliated with or endorsed by the United Nations.</p>
<h2>Sources</h2><ul>
<li><a href="https://doi.org/10.5281/zenodo.7319780">Corpus of Resolutions: UN Security Council (CR-UNSC)</a>, Seán Fobbe, Lorenzo Gasbarri and Niccolò Ridi, version 2026-08-19, CC0. Texts and metadata of resolutions 1 to 2815, derived from the UN Digital Library.</li>
<li><a href="https://github.com/UNxml/SCresolutions">Machine-readable Security Council resolutions</a> (AKN4UN XML), United Nations. Texts and metadata of resolutions adopted after January 2026. The United Nations is the source of this information.</li>
<li><a href="https://github.com/AtelierCartographie/bd-unsc">UNSC votes since 1946 database</a>, Benoît Martin, Sciences Po Atelier de cartographie and GRAM, 2026, CC BY 4.0. Every recorded vote, including vetoed and failed drafts, 1946 to {LAST_FULL}.</li>
<li>Official documents: the <a href="https://main.un.org/securitycouncil/en">Security Council website</a>, the <a href="https://digitallibrary.un.org">UN Digital Library</a> and the <a href="https://www.un.org/securitycouncil/content/repertoire">Repertoire of the Practice of the Security Council</a>.</li></ul>
<h2>Method</h2>
<p><b>Eras</b> follow political breaks. The opening events are history; every figure is computed from the documents.</p>
<p><b>Terms</b> such as "threat to the peace", "act of aggression" or "Acting under Chapter VII" are counted with text patterns that allow for scanning errors, and checked by hand on samples. A count means the phrase appears in the text, not necessarily as a formal finding; "breach of the peace" is counted only where the Council determines or states that a breach exists.</p>
<p><b>Themes</b> (women, children, civilians and others) mark resolutions whose text mentions the subject.</p>
<p><b>Regions</b> come from the resolution title: the region of the situation it concerns. Admissions, elections and appointments are "institutional"; general subjects are "thematic".</p>
<p><b>Votes</b> come from the Sciences Po database. Unanimous means every member present voted yes. A contested vote is one with any no vote or abstention, or a draft that failed. Vetoes are counted as no votes by permanent members on vetoed drafts, so a draft vetoed by two members counts for both. China's seat was held by the Republic of China until October 1971; the Soviet seat passed to the Russian Federation in December 1991.</p>
<p><b>Citations</b> between resolutions come from the CR-UNSC citation network.</p>
<h2>Corrections and reuse</h2><p>This site, its data and its code are in the public domain. Errors in the underlying documents are reproduced as published; spotted a problem in ours? Write to daniel.desposito@gmail.com.</p>'''
    expl = f'''<p class="kicker">Explainer</p><h1>What is the UN Security Council?</h1>
<p class="lede">The Security Council is the organ of the United Nations with primary responsibility for international peace and security. Under Article 25 of the UN Charter, all member states agree to carry out its decisions.</p>
<h2>Members</h2><p>Fifteen members: five permanent (China, France, Russia, the United Kingdom and the United States) and ten elected by the General Assembly for two-year terms. The Council had eleven members until the Charter amendment of 1965 enlarged it. The presidency rotates every month. <a href="/votes/">Current members and voting records</a>.</p>
<h2>How it decides</h2><p>A resolution needs nine votes in favour and no veto from a permanent member. <a href="/themes/the-veto/">What veto power is, and every veto since 1946</a>.</p>
<h2>What it can do</h2><p>Under Chapter VI of the Charter the Council recommends ways to settle disputes peacefully. Under Chapter VII, once it determines a "threat to the peace, breach of the peace, or act of aggression" (Article 39), it can impose binding measures: sanctions, arms embargoes, peace operations, tribunals, and the use of force by member states. <a href="/themes/language-of-threat/">How the Council used those three words</a> and <a href="/themes/from-advising-to-ordering/">how Chapter VII became routine</a>.</p>
<h2>In numbers</h2><div class="stats"><div><b>{fmt(len(R))}</b><span>resolutions adopted, 1946 to 2026</span></div><div><b>{TOTAL_VETOED}</b><span>drafts vetoed</span></div><div><b>{Y[LAST_FULL]["n"]}</b><span>resolutions in {LAST_FULL}</span></div><div><b>{Y[LAST_FULL]["u"]}%</b><span>adopted unanimously in {LAST_FULL}</span></div></div>
<p>Official information: the <a href="https://main.un.org/securitycouncil/en">Security Council website</a>.</p>'''
    write('/about/security-council/', page('/about/security-council/', 'What is the UN Security Council? Members, veto and powers', 'What the UN Security Council is: its 15 members, the five permanent members and veto power, how it decides, and what Chapter VII allows.', expl, crumbs=[('/', 'Home'), ('/about/', 'About'), (None, 'What is the Security Council?')]))
    write('/about/', page('/about/', 'About, sources and method', 'Sources, method and limits of Security Council Record, an independent record of UN Security Council resolutions and votes.', about))
    open(os.path.join(DIST, '404.html'), 'w').write(page('/404', 'Page not found', 'Page not found.', '<h1>Page not found</h1><p>Try the <a href="/search/">search</a> or the <a href="/resolutions/">list of resolutions</a>.</p>', index=False))

home(); eras_pages(); theme_pages(); votes_pages(); resolution_pages(); misc_pages()

# sitemap, robots
sm = ''.join(f'<url><loc>{SITE}{p}</loc></url>' for p in pages)
open(os.path.join(DIST, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
open(os.path.join(DIST, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
open(os.path.join(DIST, '_headers'), 'w').write('/assets/*\n  Cache-Control: public, max-age=604800\n/pagefind/*\n  Cache-Control: public, max-age=86400\n')
json.dump(dict(eras=ES and [{k: v for k, v in x.items() if k != 'top'} for x in ES], years=Y, agree=AGREE, veto_total=VETO_TOTAL, agg_targets=AGG_TARGETS, breach=[r['n'] for r in BREACH]), open(os.path.join(HERE, 'build', 'stats.json'), 'w'), default=str, indent=1)
print(len(pages), 'pages')

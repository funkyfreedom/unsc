"""Write the open data tables to data/ and copy them to dist/data/ for download."""
import csv, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

D = json.load(open(os.path.join(BUILD, 'data.json')))
S = json.load(open(os.path.join(BUILD, 'stats.json')))
R, DR, ERAS, C = D['resolutions'], D['drafts'], D['eras'], D['countries']
THEMES = dict(D['themes'])
NAME = {c['key']: c['name'] for c in C}
os.makedirs(DATA, exist_ok=True)
SITE = 'https://securitycouncilrecord.org'

def write(name, header, rows):
    with open(os.path.join(DATA, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return len(rows)

yn = lambda b: '' if b is None else ('yes' if b else 'no')
n1 = write('resolutions.csv',
    ['resolution', 'symbol', 'date', 'year', 'era', 'subject', 'region', 'countries', 'votes_yes', 'votes_no', 'abstentions', 'not_voting', 'unanimous',
     'acting_under_chapter_vii', 'threat_to_the_peace', 'breach_of_the_peace', 'act_of_aggression', 'word_aggression', 'word_decides', 'all_necessary_means',
     'themes', 'words', 'cites', 'cited_by', 'official_document', 'page'],
    [[r['n'], r['sym'], r['date'], r['year'], ERAS[r['era']]['name'], r['topic'], r['region'], '; '.join(r['countries']), r['yes'], r['no'], r['abst'], r['nonvote'], yn(r['unanimous']),
      yn(r['flags']['ch7']), yn(r['flags']['threat']), yn(r['flags']['breach']), yn(r['flags']['act_aggression']), yn(r['flags']['aggression']), yn(r['flags']['decides']), yn(r['flags']['all_necessary']),
      '; '.join(THEMES[t] for t in r['themes']), r['words'], ' '.join(map(str, r['cites'])), len(r['cited_by']), r['url_en'], f'{SITE}/resolutions/{r["n"]}/'] for r in R])

VOTE = {'Y': 'yes', 'N': 'no', 'A': 'abstained', 'NV': 'did not vote', '?': 'unknown'}
rows = []
for r in R:
    for k, v in sorted(r['member_votes'].items()):
        rows.append([r['date'], r['sym'], 'adopted', r['n'], NAME.get(k, k), VOTE.get(v, v)])
for d in DR:
    for k, v in sorted(d['votes'].items()):
        rows.append([d['date'], ' '.join(d['symbol'].split()), d['outcome'].replace('lack of maj.', 'not enough votes'), '', NAME.get(k, k), VOTE.get(v, v)])
rows.sort(key=lambda x: (x[0], x[1], x[4]))
n2 = write('votes.csv', ['date', 'document', 'outcome', 'resolution', 'country', 'vote'], rows)

n3 = write('drafts.csv', ['date', 'document', 'subject', 'outcome', 'votes_yes', 'votes_no', 'abstentions', 'vetoed_by'],
    [[d['date'], ' '.join(d['symbol'].split()), ' '.join(d['title'].split()), d['outcome'].replace('lack of maj.', 'not enough votes'), d['yes'], d['no'], d['abst'], '; '.join(d['vetoed_by'])] for d in sorted(DR, key=lambda d: d['date'])])

n4 = write('citations.csv', ['citing_resolution', 'cited_resolution'], [[r['n'], c] for r in R for c in r['cites']])

P5 = ['RUSSIAN FEDERATION/USSR', 'UNITED STATES', 'UNITED KINGDOM', 'FRANCE', 'CHINA']
n5 = write('eras.csv',
    ['era', 'from', 'to', 'opened_by', 'resolutions', 'per_year', 'unanimous_pct', 'vetoed_drafts', 'failed_drafts', 'chapter_vii_pct', 'threat_to_the_peace_pct', 'word_aggression_pct', 'word_decides_pct',
     'median_words', 'vetoes_russia_ussr', 'vetoes_united_states', 'vetoes_united_kingdom', 'vetoes_france', 'vetoes_china'],
    [[e['name'], e['a'], e['b'], S['opened'][i], s['n'], s['per_year'], s['unan'], s['vetoed'], s['failed'], s['flags']['ch7'], s['flags']['threat'], s['flags']['aggression'], s['flags']['decides'],
      s['words']] + [s['vetoN'][k] for k in P5] for i, (e, s) in enumerate(zip(ERAS, S['eras']))])

n6 = write('countries.csv', ['country', 'permanent_member', 'years_with_votes', 'first_year', 'last_year', 'yes_on_adopted', 'abstentions_on_adopted', 'no_on_adopted', 'no_on_failed_or_vetoed', 'page'],
    [[c['name'], 'yes' if c['p5'] else 'no', len(c['years']), c['years'][0], c['years'][-1], c['counts'].get('adopted|Y', 0), c['counts'].get('adopted|A', 0), c['counts'].get('adopted|N', 0),
      c['counts'].get('vetoed|N', 0) + c['counts'].get('lack of maj.|N', 0), f'{SITE}/votes/{c["slug"]}/'] for c in sorted(C, key=lambda c: c['name'])])

out = os.path.join(DIST, 'data')
os.makedirs(out, exist_ok=True)
for f in os.listdir(DATA):
    if f.endswith('.csv'):
        shutil.copy(os.path.join(DATA, f), out)
print(f'resolutions {n1}, votes {n2}, drafts {n3}, citations {n4}, eras {n5}, countries {n6}')

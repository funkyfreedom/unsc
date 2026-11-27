"""Templates, styles and SVG charts for Security Council Record."""
import html, json

SITE = 'https://securitycouncilrecord.org'
NAME = 'Security Council Record'
BLUE = '#2c78d4'
GREY = '#c4c3b6'
ORANGE = '#e8693b'
GRID = '#e9e8e3'
TEXT = '#1d1d1b'
MUTED = '#6b6a64'

def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)

def fmt(n):
    return f'{n:,}'

CSS = r"""
@font-face{font-family:'Inter';src:url('/assets/fonts/inter-latin-wght-normal.woff2') format('woff2');font-weight:100 900;font-display:swap;unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:'Inter';src:url('/assets/fonts/inter-latin-ext-wght-normal.woff2') format('woff2');font-weight:100 900;font-display:swap;unicode-range:U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}
:root{--blue:#2c78d4;--blue-ink:#1d5fae;--grey:#c4c3b6;--band:#f6f6f3;--rule:#e6e5df;--text:#1d1d1b;--muted:#6b6a64;--orange:#e8693b;--max:780px;--wide:1040px}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#fff;color:var(--text);font:16px/1.6 Inter,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;font-feature-settings:'cv11','ss01';text-rendering:optimizeLegibility}
a{color:var(--blue-ink);text-decoration:none;border-bottom:1px solid #c9dcf3}
a:hover{border-bottom-color:var(--blue)}
a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid var(--blue);outline-offset:2px;border-radius:2px}
.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;background:#fff;padding:8px 12px;z-index:9}
header.site{border-bottom:1px solid var(--rule)}
.bar{max-width:var(--wide);margin:0 auto;padding:14px 20px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;color:var(--text);border:0;font-weight:650;letter-spacing:-.01em;font-size:17px}
.brand svg{flex:none}
nav.main{display:flex;gap:18px;flex-wrap:wrap;margin-left:auto;font-size:14.5px}
nav.main a{color:var(--muted);border:0}
nav.main a:hover,nav.main a[aria-current]{color:var(--text)}
main{max-width:var(--max);margin:0 auto;padding:28px 20px 60px}
main.wide{max-width:var(--wide)}
h1{font-size:34px;line-height:1.18;letter-spacing:-.02em;margin:18px 0 10px;font-weight:700}
h2{font-size:23px;line-height:1.3;letter-spacing:-.01em;margin:46px 0 12px;font-weight:650}
h3{font-size:18px;margin:30px 0 8px;font-weight:620}
p{margin:0 0 14px}
.lede{font-size:19px;color:#3c3b37;line-height:1.55}
.muted,.meta{color:var(--muted)}
.meta{font-size:14px}
.kicker{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-top:8px}
.crumbs{font-size:14px;color:var(--muted)}
.crumbs a{color:var(--muted);border:0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);margin:22px 0}
.stats div{background:#fff;padding:14px 16px}
.stats b{display:block;font-size:26px;font-weight:650;letter-spacing:-.02em}
.stats span{font-size:13.5px;color:var(--muted)}
ol.findings{padding-left:22px}
ol.findings li{margin:0 0 14px}
ol.findings li a.more{font-size:14px;white-space:nowrap}
figure{margin:26px 0}
figure svg{width:100%;height:auto;display:block}
figure svg text{font-family:Inter,system-ui,sans-serif}
figcaption{font-size:13px;color:var(--muted);margin-top:6px}
.tw{overflow-x:auto;margin:18px 0;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:14.5px;line-height:1.45}
th,td{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid var(--rule)}
th{font-weight:600;font-size:13px;color:var(--muted);border-bottom:1px solid #cfcec7;white-space:nowrap}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:nth-child(even) td{background:var(--band)}
.eras td:first-child{min-width:170px}
.bleed{width:min(var(--wide),calc(100vw - 40px));position:relative;left:50%;transform:translateX(-50%)}
.search-hero{display:flex;gap:8px;margin:22px 0 8px}
.search-hero input,.q{flex:1;font:inherit;font-size:17px;padding:12px 14px;border:1px solid #cfcec7;border-radius:6px;min-width:0}
button,.btn{font:inherit;font-size:15px;font-weight:600;background:var(--blue);color:#fff;border:0;border-radius:6px;padding:11px 18px;cursor:pointer}
.btn{display:inline-block;border:0}
.btn.light{background:var(--band);color:var(--text)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.chip{font-size:13px;background:var(--band);border:1px solid var(--rule);color:var(--text);padding:3px 10px;border-radius:99px}
a.chip:hover{border-color:var(--grey)}
.badge{display:inline-block;font-size:12.5px;font-weight:600;padding:2px 8px;border-radius:4px;background:#e8f0fb;color:var(--blue-ink);margin:0 6px 6px 0}
.badge.orange{background:#fcebe3;color:#a8441c}
.badge.grey{background:var(--band);color:var(--muted)}
.vote{display:flex;gap:16px;flex-wrap:wrap;font-size:15px;margin:8px 0 4px}
.vote b{font-weight:650}
.text{font-family:'Iowan Old Style','Charter','Georgia',serif;font-size:17px;line-height:1.65;border-top:1px solid var(--rule);margin-top:26px;padding-top:12px}
.text p{margin:0 0 12px}
.cols{columns:2 260px;column-gap:28px}
.cols li{break-inside:avoid}
ul.plain{list-style:none;padding:0;margin:0}
ul.plain li{padding:6px 0;border-bottom:1px solid var(--rule)}
.yearnav{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:14px}
.note{font-size:14px;background:var(--band);border-left:3px solid var(--grey);padding:10px 14px;margin:20px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:18px 0}
.card{border:1px solid var(--rule);border-radius:8px;padding:16px;color:var(--text);display:block}
.card:hover{border-color:var(--grey)}
.card b{display:block;margin-bottom:4px}
.card span{font-size:14px;color:var(--muted)}
footer.site{border-top:1px solid var(--rule);background:var(--band);font-size:14px;color:var(--muted)}
footer.site .bar{display:block;padding:26px 20px 34px}
footer.site p{margin:0 0 8px;max-width:760px}
/* search */
.sgrid{display:grid;grid-template-columns:230px 1fr;gap:30px;margin-top:18px}
.facets fieldset{border:0;padding:0;margin:0 0 18px}
.facets legend{font-size:13px;font-weight:600;color:var(--muted);margin-bottom:6px}
.facets label{display:flex;gap:7px;align-items:flex-start;font-size:14px;padding:2px 0;cursor:pointer}
.facets label small{color:var(--muted);margin-left:auto;font-variant-numeric:tabular-nums}
.results .r{padding:14px 0;border-bottom:1px solid var(--rule)}
.results .r a{font-weight:600;border:0}
.results .r p{margin:4px 0 0;font-size:14.5px;color:#3c3b37}
.results mark{background:#e8f0fb;color:inherit;padding:0 1px}
.count{font-size:14px;color:var(--muted);margin:6px 0}
@media (max-width:760px){h1{font-size:27px}.lede{font-size:17px}.sgrid{grid-template-columns:1fr}.facets{order:2}nav.main{margin-left:0;gap:14px}main{padding-top:18px}}
@media print{header.site nav,footer.site,.search-hero{display:none}a{border:0;color:inherit}}
"""

LOGO = f'''<svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true"><rect width="28" height="28" rx="5" fill="{BLUE}"/><rect x="6" y="15" width="3.6" height="7" fill="#fff"/><rect x="12.2" y="10" width="3.6" height="12" fill="#fff"/><rect x="18.4" y="6" width="3.6" height="16" fill="#fff"/></svg>'''

NAV = [('/eras/', 'Eras'), ('/themes/', 'Themes'), ('/votes/', 'Votes'), ('/resolutions/', 'Resolutions'), ('/language/', 'Language lab'), ('/search/', 'Search'), ('/about/', 'About')]

def page(path, title, desc, body, *, wide=False, jsonld=None, index=True, head_extra='', pagefind=False, filters=None, crumbs=None, h1_title=None):
    canonical = SITE + path
    full_title = title if title == NAME else f'{title} | {NAME}'
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if path.startswith(h) else ""}>{t}</a>' for h, t in NAV)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ''
    robots = '' if index else '<meta name="robots" content="noindex">'
    fl = ''
    if filters:
        fl = '<div data-pagefind-ignore hidden>' + ''.join(f'<span data-pagefind-filter="{e(k)}">{e(v)}</span>' for k, vs in filters.items() for v in (vs if isinstance(vs, list) else [vs])) + '</div>'
    pf = ' data-pagefind-body' if pagefind else ''
    cr = ''
    if crumbs:
        cr = '<div class="crumbs" data-pagefind-ignore>' + ' / '.join(f'<a href="{h}">{e(t)}</a>' if h else e(t) for h, t in crumbs) + '</div>'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/share.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
{ld}{head_extra}
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="site"><div class="bar"><a class="brand" href="/" aria-label="{NAME}, home">{LOGO}<span>{NAME}</span></a><nav class="main" aria-label="Main">{nav}</nav></div></header>
<main id="content"{' class="wide"' if wide else ''}{pf}>{cr}{fl}
{body}
</main>
<footer class="site"><div class="bar">
<p><b>{NAME}</b> is an independent record of every resolution, vote and veto of the United Nations Security Council since 1946. It is not affiliated with or endorsed by the United Nations. For official documents, use the <a href="https://main.un.org/securitycouncil/en">Security Council website</a> and the <a href="https://digitallibrary.un.org">UN Digital Library</a>.</p>
<p>Built on the documentation of the Security Council, the <a href="https://doi.org/10.5281/zenodo.7319780">CR-UNSC corpus</a> (Fobbe, Gasbarri and Ridi, CC0), the <a href="https://github.com/UNxml/SCresolutions">UN machine-readable resolutions</a> and the <a href="https://github.com/AtelierCartographie/bd-unsc">UNSC votes since 1946 database</a> (Sciences Po Atelier de cartographie and GRAM, CC BY 4.0). <a href="/about/">Method and sources</a>.</p>
<p>Made by Daniel D'Esposito. Designed to work on any phone and with screen readers. Content in the public domain.</p>
</div></footer>
</body>
</html>'''

# ---------------- charts ----------------
def _t(x, y, s, size=11, fill=MUTED, anchor='start', weight=None, extra=''):
    w = f' font-weight="{weight}"' if weight else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{w}{extra}>{e(s)}</text>'

def chart_frame(w, h, title, sub, inner, label):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}"><title>{e(label)}</title>{_t(0, 22, title, 16, TEXT, weight=600)}{_t(0, 42, sub, 12)}{inner}</svg>'

def timeline_chart(years, eras, title, sub, highlight=()):
    """years: list of dict(y, n, u) ; eras: list of dict(a,b,short)"""
    left, right, y0, h1 = 44, 740, 100, 200
    b1 = y0 + h1; t2, h2 = 336, 110; b2 = t2 + h2
    ys0, yN = years[0]['y'], years[-1]['y']
    band = (right - left) / (yN - ys0 + 1)
    x = lambda yr: left + (yr - ys0) * band
    nmax = max(100, max(r['n'] for r in years))
    sy = lambda v: b1 - v / nmax * h1
    su = lambda v: b2 - v / 100 * h2
    parts = []
    for i, er in enumerate(eras):
        if er['b'] < ys0 or er['a'] > yN:
            continue
        a, b = max(er['a'], ys0), min(er['b'], yN)
        if i % 2 == 0:
            parts.append(f'<rect x="{x(a):.1f}" y="{y0-36}" width="{(b-a+1)*band:.1f}" height="{b2-y0+36}" fill="{GREY}" fill-opacity="0.13"/>')
        words = er['short'].split(' ', 1) if (b - a + 1) * band < len(er['short']) * 5.8 + 8 else [er['short']]
        parts.append(f'<text x="{x(a)+3:.1f}" y="{y0-22}" font-size="10" fill="{MUTED}"><tspan>{e(words[0])}</tspan>' + (f'<tspan x="{x(a)+3:.1f}" dy="12">{e(words[1])}</tspan>' if len(words) > 1 else '') + '</text>')
    for v in (0, 25, 50, 75, 100):
        parts.append(f'<line x1="{left}" x2="{right}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="{GRID}"/>' + _t(left - 6, sy(v) + 4, v, 11, MUTED, 'end'))
    peak = max(years, key=lambda r: r['n'])
    last = years[-1]
    for r in years:
        col = BLUE if r['y'] in (peak['y'], last['y']) or r['y'] in highlight else GREY
        parts.append(f'<rect x="{x(r["y"])+0.8:.1f}" y="{sy(r["n"]):.1f}" width="{max(band-1.6,1):.1f}" height="{b1-sy(r["n"]):.1f}" fill="{col}"><title>{r["y"]}: {r["n"]} resolutions</title></rect>')
    parts.append(_t(x(peak['y']) + band + 4, sy(peak['n']) + 10, f'{peak["n"]} in {peak["y"]}', 11, TEXT, weight=600))
    recent = max(r['n'] for r in years[-6:])
    if last['y'] != peak['y']:
        parts.append(_t(x(last['y']) + band, sy(recent) - 8, f'{last["n"]} in {last["y"]}', 11, TEXT, 'end', 600))
    for v in (0, 50, 100):
        parts.append(f'<line x1="{left}" x2="{right}" y1="{su(v):.1f}" y2="{su(v):.1f}" stroke="{GRID}"/>' + _t(left - 6, su(v) + 4, f'{v}%', 11, MUTED, 'end'))
    pts = [r for r in years if r.get('u') is not None]
    d = ' '.join(f'{"M" if i == 0 else "L"}{x(r["y"])+band/2:.1f},{su(r["u"]):.1f}' for i, r in enumerate(pts))
    parts.append(f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="1.6"/>')
    for r in pts:
        parts.append(f'<circle cx="{x(r["y"])+band/2:.1f}" cy="{su(r["u"]):.1f}" r="3" fill="{BLUE}" fill-opacity="0"><title>{r["y"]}: {r["u"]}% unanimous</title></circle>')
    lu = pts[-1]
    parts.append(_t(x(lu['y']) + band / 2, su(lu['u']) + 16, f'{lu["u"]}% in {lu["y"]}', 11, TEXT, 'end', 600))
    step = 10 if yN - ys0 > 30 else (2 if yN - ys0 > 8 else 1)
    for v in range(((ys0 + step - 1) // step) * step, yN + 1, step):
        parts.append(_t(x(v) + band / 2, b2 + 18, v, 11, MUTED, 'middle'))
    parts.append(_t(left, t2 - 10, 'share adopted unanimously', 10, MUTED))
    return chart_frame(760, 480, title, sub, ''.join(parts), title)

def era_lines_chart(eras_labels, series, title, sub, note=None, right_pad=200, peak_note=None):
    """series: list of dict(key,name,values(list or None),color,width,dash,bold)"""
    left, right, y0, h = 50, 760 - right_pad, 70, 290
    base = y0 + h
    n = len(eras_labels)
    step = (right - left) / (n - 1)
    x = lambda i: left + i * step
    y = lambda v: base - v / 100 * h
    parts = []
    for v in (0, 25, 50, 75, 100):
        parts.append(f'<line x1="{left}" x2="{right}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{GRID}"/>' + _t(left - 8, y(v) + 4, f'{v}%', 11, MUTED, 'end'))
    for i, lab in enumerate(eras_labels):
        parts.append(_t(x(i), base + 20, lab, 10, MUTED, 'middle'))
    ends = []
    for s in series:
        pts = [(i, v) for i, v in enumerate(s['values']) if v is not None]
        d = ' '.join(f'{"M" if k == 0 else "L"}{x(i):.1f},{y(v):.1f}' for k, (i, v) in enumerate(pts))
        dash = f' stroke-dasharray="{s["dash"]}"' if s.get('dash') else ''
        parts.append(f'<path d="{d}" fill="none" stroke="{s["color"]}" stroke-width="{s.get("width", 1.8)}"{dash}/>')
        for i, v in pts:
            parts.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3" fill="{s["color"]}"><title>{e(s["name"])}, {e(eras_labels[i])}: {v}%</title></circle>')
        ends.append([y(pts[-1][1]), s, pts[-1][1]])
    ends.sort(key=lambda t: t[0])
    for k in range(1, len(ends)):
        if ends[k][0] - ends[k - 1][0] < 15:
            ends[k][0] = ends[k - 1][0] + 15
    for yy, s, v in ends:
        parts.append(_t(right + 10, yy + 4, f'{s["name"]} {v}%', 11, s['color'] if s.get('bold') else MUTED, 'start', 600 if s.get('bold') else None))
    if peak_note:
        i, v, txt, col = peak_note
        parts.append(_t(x(i), y(v) - 10, f'{v}%', 11, col, 'middle', 600))
        parts.append(_t(x(i) + 18, y(v) - 10, txt, 10, MUTED))
    if note:
        parts.append(_t(left, base + 44, note, 10, MUTED))
    return chart_frame(760, 430 if note else 410, title, sub, ''.join(parts), title)

def small_multiples(members, eras_labels, title, sub):
    """members: list of dict(name, values)"""
    left, right, y0, rowH, barMax = 140, 740, 70, 62, 44
    step = (right - left) / len(eras_labels)
    bw = step * 0.62
    vmax = max(max(m['values']) for m in members) or 1
    parts = []
    for mi, m in enumerate(members):
        base = y0 + (mi + 1) * rowH
        pk = max(range(len(m['values'])), key=lambda i: m['values'][i])
        parts.append(_t(0, base - 14, m['name'], 12, TEXT, weight=600))
        parts.append(_t(0, base, f'{sum(m["values"])} in total', 11, MUTED))
        parts.append(f'<line x1="{left}" x2="{right}" y1="{base}" y2="{base}" stroke="#b9b8ae"/>')
        for i, v in enumerate(m['values']):
            hh = v / vmax * barMax
            col = BLUE if i == pk and v > 0 else GREY
            parts.append(f'<rect x="{left+i*step+(step-bw)/2:.1f}" y="{base-hh:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{col}"><title>{e(m["name"])}, {e(eras_labels[i])}: {v}</title></rect>')
            if v:
                parts.append(_t(left + i * step + step / 2, base - hh - 4, v, 10, TEXT if i == pk else MUTED, 'middle', 600 if i == pk else None))
    for i, lab in enumerate(eras_labels):
        parts.append(_t(left + i * step + step / 2, y0 + len(members) * rowH + 18, lab, 10, MUTED, 'middle'))
    return chart_frame(760, y0 + len(members) * rowH + 34, title, sub, ''.join(parts), title)

def stacked_chart(rows, cats, title, sub, accent=0):
    """rows: list of (label, {cat: value}) ; cats: ordered list"""
    left, right, y0, bh, gap = 92, 740, 96, 30, 12
    W = right - left
    ops = [1, .85, .68, .52, .4, .3, .2, .12, .08]
    parts = []
    for ci, c in enumerate(cats):
        col = BLUE if ci == accent else GREY
        op = 0.8 if ci == accent else ops[ci]
        parts.append(f'<rect x="{left+ci*81}" y="58" width="10" height="10" fill="{col}" fill-opacity="{op}"/>' + _t(left + ci * 81 + 14, 67, c, 11))
    for ri, (lab, vals) in enumerate(rows):
        by = y0 + ri * (bh + gap)
        tot = sum(vals.values()) or 1
        acc = 0
        parts.append(_t(left - 8, by + bh / 2 + 4, lab, 11, MUTED, 'end'))
        for ci, c in enumerate(cats):
            v = vals.get(c, 0)
            x0 = left + acc / tot * W
            w = v / tot * W
            acc += v
            pct = round(100 * v / tot)
            col = BLUE if ci == accent else GREY
            op = 0.8 if ci == accent else ops[ci]
            parts.append(f'<rect x="{x0:.1f}" y="{by}" width="{max(w-1.5,0):.1f}" height="{bh}" fill="{col}" fill-opacity="{op}"><title>{e(lab)}, {e(c)}: {pct}%</title></rect>')
            if pct >= 8:
                parts.append(_t(x0 + 5, by + bh / 2 + 4, f'{pct}%', 11, TEXT, weight=600 if ci == accent else None))
    return chart_frame(760, y0 + len(rows) * (bh + gap) + 10, title, sub, ''.join(parts), title)

def bars_chart(items, title, sub, accent_keys=(), unit=''):
    """items: list of (label, value). Vertical bars, labels under."""
    left, right, y0, h = 40, 740, 70, 200
    base = y0 + h
    n = len(items)
    step = (right - left) / n
    vmax = max(v for _, v in items) or 1
    parts = []
    for i, (lab, v) in enumerate(items):
        hh = v / vmax * h
        col = BLUE if lab in accent_keys else GREY
        parts.append(f'<rect x="{left+i*step+step*0.12:.1f}" y="{base-hh:.1f}" width="{step*0.76:.1f}" height="{hh:.1f}" fill="{col}"><title>{e(lab)}: {v}{unit}</title></rect>')
        if n <= 16 or lab in accent_keys:
            parts.append(_t(left + i * step + step / 2, base - hh - 4, f'{v}{unit}', 10, TEXT if lab in accent_keys else MUTED, 'middle'))
        if n <= 16 or i % max(1, n // 8) == 0:
            parts.append(_t(left + i * step + step / 2, base + 16, lab, 10, MUTED, 'middle'))
    parts.append(f'<line x1="{left}" x2="{right}" y1="{base}" y2="{base}" stroke="#b9b8ae"/>')
    return chart_frame(760, base + 30, title, sub, ''.join(parts), title)

def hbars_chart(items, title, sub, accent=0):
    """items: list of (label, value, href) horizontal bars."""
    left, right, y0, bh, gap = 200, 700, 64, 18, 8
    vmax = max(v for _, v, _ in items) or 1
    parts = []
    for i, (lab, v, _) in enumerate(items):
        by = y0 + i * (bh + gap)
        w = v / vmax * (right - left)
        col = BLUE if i < accent else GREY
        parts.append(_t(left - 8, by + 13, lab, 11, TEXT, 'end'))
        parts.append(f'<rect x="{left}" y="{by}" width="{w:.1f}" height="{bh}" fill="{col}"><title>{e(lab)}: {v}</title></rect>')
        parts.append(_t(left + w + 6, by + 13, v, 11, MUTED))
    return chart_frame(760, y0 + len(items) * (bh + gap) + 10, title, sub, ''.join(parts), title)

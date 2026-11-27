// Language lab: share of resolutions per year that contain a word or phrase.
const pagefind = await import('/pagefind/pagefind.js');
await pagefind.filters();
const totals = await (await fetch('/assets/years.json')).json();
const years = Object.keys(totals).map(Number).sort((a, b) => a - b);
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const BLUE = '#2c78d4', GREY = '#c4c3b6', GRID = '#e9e8e3', MUTED = '#6b6a64', TEXT = '#1d1d1b';

function chart(q, counts, found) {
  const left = 44, right = 740, y0 = 70, h = 230, base = y0 + h;
  const band = (right - left) / years.length;
  const share = years.map((y) => ({ y, n: counts[y] || 0, s: totals[y] ? (100 * (counts[y] || 0)) / totals[y] : 0 }));
  const max = Math.max(10, ...share.map((d) => d.s));
  const top = Math.ceil(max / 10) * 10;
  const sy = (v) => base - (v / top) * h;
  const peak = share.reduce((a, b) => (b.s > a.s ? b : a), share[0]);
  let p = `<text x="0" y="22" font-size="16" font-weight="600" fill="${TEXT}">"${esc(q)}": in ${found.toLocaleString('en-US')} resolutions</text>`;
  p += `<text x="0" y="42" font-size="12" fill="${MUTED}">Share of resolutions adopted each year whose text matches, 1946 to ${years[years.length - 1]}</text>`;
  for (const v of [0, top / 2, top]) p += `<line x1="${left}" x2="${right}" y1="${sy(v)}" y2="${sy(v)}" stroke="${GRID}"/><text x="${left - 6}" y="${sy(v) + 4}" font-size="11" fill="${MUTED}" text-anchor="end">${Math.round(v)}%</text>`;
  share.forEach((d, i) => {
    const hh = base - sy(d.s);
    p += `<rect x="${left + i * band + 0.8}" y="${sy(d.s)}" width="${Math.max(band - 1.6, 1)}" height="${hh}" fill="${d.y === peak.y && d.s > 0 ? BLUE : GREY}"><title>${d.y}: ${d.n} of ${totals[d.y]} resolutions (${Math.round(d.s)}%)</title></rect>`;
  });
  if (peak.s > 0) p += `<text x="${left + years.indexOf(peak.y) * band + band / 2}" y="${sy(peak.s) - 6}" font-size="11" font-weight="600" fill="${TEXT}" text-anchor="middle">${Math.round(peak.s)}% in ${peak.y}</text>`;
  for (let y = 1950; y <= years[years.length - 1]; y += 10) p += `<text x="${left + years.indexOf(y) * band + band / 2}" y="${base + 18}" font-size="11" fill="${MUTED}" text-anchor="middle">${y}</text>`;
  return `<svg viewBox="0 0 760 330" role="img" aria-label="Share of resolutions per year using ${esc(q)}">${p}</svg><figcaption>Hover a bar for the count. Source: full text of all resolutions.</figcaption>`;
}

async function run(raw) {
  const q = raw.trim();
  if (!q) return;
  history.replaceState(null, '', `?q=${encodeURIComponent(q)}`);
  $('lq').value = q;
  const term = q.includes(' ') && !q.startsWith('"') ? `"${q}"` : q;
  $('lchart').innerHTML = '<p class="muted">Counting…</p>';
  const search = await pagefind.search(term, { filters: { type: ['Resolution'] } });
  const counts = search.filters?.year || {};
  $('lchart').innerHTML = chart(q.replace(/"/g, ''), counts, search.results.length);
  const first = await Promise.all(search.results.slice(0, 12).map((r) => r.data()));
  $('llist').innerHTML = search.results.length
    ? `<h2>Most relevant matches</h2><ul class="plain">${first.map((d) => `<li><a href="${esc(d.url)}">${esc(d.meta?.title)}</a> <span class="muted">${esc(d.meta?.topic || '')}</span></li>`).join('')}</ul><p><a href="/search/?q=${encodeURIComponent(term)}">See all ${search.results.length.toLocaleString('en-US')} in Super search</a></p>`
    : '<p>No resolution uses this word.</p>';
}

$('lform').addEventListener('submit', (ev) => { ev.preventDefault(); run($('lq').value); });
document.querySelectorAll('[data-q]').forEach((b) => b.addEventListener('click', () => run(b.dataset.q)));
run(new URLSearchParams(location.search).get('q') || 'aggression');

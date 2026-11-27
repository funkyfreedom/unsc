// Super search: Pagefind full-text search with facets.
const pagefind = await import('/pagefind/pagefind.js');
await pagefind.options({ excerptLength: 28 });

const FACETS = [
  ['type', 'Type'], ['era', 'Era'], ['region', 'Region'], ['charter', 'Charter wording'],
  ['theme', 'Theme'], ['vote', 'Vote'], ['country', 'Country'],
];
const ORDER_BY_LABEL = new Set(['era']);
const PAGE = 20;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const params = new URLSearchParams(location.search);
let q = params.get('q') || '';
const sel = Object.fromEntries(FACETS.map(([k]) => [k, new Set(params.getAll(k))]));
let results = [], shown = 0, allFilters = await pagefind.filters();
$('q').value = q;

function filterObj() {
  const f = {};
  for (const [k] of FACETS) if (sel[k].size) f[k] = { any: [...sel[k]] };
  return f;
}

function syncUrl() {
  const p = new URLSearchParams();
  if (q) p.set('q', q);
  for (const [k] of FACETS) for (const v of sel[k]) p.append(k, v);
  history.replaceState(null, '', p.toString() ? `?${p}` : location.pathname);
}

function renderFacets(counts) {
  const html = FACETS.map(([k, label]) => {
    const base = allFilters[k] || {};
    let vals = Object.keys(base);
    if (!vals.length) return '';
    const c = counts?.[k] || {};
    vals.sort(ORDER_BY_LABEL.has(k) ? undefined : (a, b) => (c[b] ?? 0) - (c[a] ?? 0) || (base[b] - base[a]));
    if (k === 'country') vals = vals.filter((v) => (c[v] ?? 0) > 0 || sel[k].has(v)).slice(0, 25);
    const items = vals.map((v) => `<label><input type="checkbox" data-k="${esc(k)}" value="${esc(v)}" ${sel[k].has(v) ? 'checked' : ''}><span>${esc(v)}</span><small>${(c[v] ?? 0).toLocaleString('en-US')}</small></label>`).join('');
    return items ? `<fieldset><legend>${esc(label)}</legend>${items}</fieldset>` : '';
  }).join('');
  $('facets').innerHTML = html;
}

async function showMore() {
  const slice = results.slice(shown, shown + PAGE);
  const data = await Promise.all(slice.map((r) => r.data()));
  $('results').insertAdjacentHTML('beforeend', data.map((d) => {
    const t = d.meta?.title || d.url;
    const topic = d.meta?.topic ? ` <span class="muted">${esc(d.meta.topic)}</span>` : '';
    return `<div class="r"><a href="${esc(d.url)}">${esc(t)}</a>${topic}<p>${d.excerpt || ''}</p></div>`;
  }).join(''));
  shown += slice.length;
  $('more').hidden = shown >= results.length;
}

async function run() {
  syncUrl();
  const f = filterObj();
  if (!q && !Object.keys(f).length) {
    $('count').textContent = 'Type a word, a phrase in quotes, or pick a filter.';
    $('results').innerHTML = ''; $('more').hidden = true;
    renderFacets(allFilters);
    return;
  }
  const search = await pagefind.search(q || null, { filters: f });
  results = search.results; shown = 0;
  $('results').innerHTML = '';
  $('count').textContent = `${results.length.toLocaleString('en-US')} ${results.length === 1 ? 'result' : 'results'}`;
  renderFacets(search.filters);
  await showMore();
}

$('sform').addEventListener('submit', (ev) => { ev.preventDefault(); q = $('q').value.trim(); run(); });
$('facets').addEventListener('change', (ev) => {
  const t = ev.target;
  if (t.dataset.k) { t.checked ? sel[t.dataset.k].add(t.value) : sel[t.dataset.k].delete(t.value); run(); }
});
$('more').addEventListener('click', showMore);
run();

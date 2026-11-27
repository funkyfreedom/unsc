// Shareable links: a "Copy link" button by every page title, and a # link on
// every section heading and resolution paragraph. Clicking one puts the full
// URL on the clipboard and in the address bar.
const toast = document.createElement('div');
toast.className = 'toast'; toast.setAttribute('role', 'status'); toast.setAttribute('aria-live', 'polite');
document.body.append(toast);
let timer;
function say(msg) { toast.textContent = msg; toast.classList.add('on'); clearTimeout(timer); timer = setTimeout(() => toast.classList.remove('on'), 1800); }
async function copy(url) {
  try { await navigator.clipboard.writeText(url); say('Link copied'); }
  catch { window.prompt('Copy this link:', url); }
}
const base = () => location.origin + location.pathname + location.search;

const h1 = document.querySelector('main h1');
if (h1 && !h1.closest('a') && location.pathname !== '/') {
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'copylink'; b.textContent = 'Copy link';
  b.setAttribute('aria-label', 'Copy the link to this page');
  b.addEventListener('click', () => copy(base()));
  h1.insertAdjacentElement('afterend', b);
}

document.querySelectorAll('main h2[id], main h3[id], main .text p[id]').forEach((el) => {
  if (el.closest('a, summary, button')) return;
  const a = document.createElement('a');
  a.className = 'anchor'; a.href = '#' + el.id; a.textContent = el.tagName === 'P' ? '¶' : '#';
  a.setAttribute('aria-label', el.tagName === 'P' ? 'Copy the link to this paragraph' : 'Copy the link to this section');
  a.addEventListener('click', (ev) => {
    ev.preventDefault();
    history.replaceState(null, '', '#' + el.id);
    el.scrollIntoView({ block: 'start' });
    copy(base() + '#' + el.id);
  });
  el.append(a);
});

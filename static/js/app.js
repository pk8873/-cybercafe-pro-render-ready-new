/* Global niceties: tilt, reveal, toast popup */
(function(){
  // Mouse-follow tilt
  document.addEventListener('mousemove', (e) => {
    document.querySelectorAll('.tilt').forEach(el => {
      const r = el.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) {
        el.style.setProperty('--rx','0deg'); el.style.setProperty('--ry','0deg'); return;
      }
      const px = (e.clientX - r.left) / r.width - .5;
      const py = (e.clientY - r.top) / r.height - .5;
      el.style.setProperty('--ry', (px * 6).toFixed(2) + 'deg');
      el.style.setProperty('--rx', (-py * 6).toFixed(2) + 'deg');
    });
  });
  // Reveal-on-scroll
  const io = new IntersectionObserver((es) => es.forEach(e => e.isIntersecting && e.target.classList.add('in')), {threshold:.08});
  document.querySelectorAll('.card-3d, .stat, .doc-tile').forEach(el => { el.classList.add('reveal'); io.observe(el); });

  // ----- Global popup toast -----
  function ensureHost(){
    let h = document.querySelector('.lv-toast-host');
    if (!h) { h = document.createElement('div'); h.className='lv-toast-host'; document.body.appendChild(h); }
    return h;
  }
  window.LV = window.LV || {};
  window.LV.toast = function(title, desc, kind){
    const host = ensureHost();
    const t = document.createElement('div');
    t.className = 'lv-toast' + (kind ? ' '+kind : '');
    const icon = kind === 'success' ? '✅' : kind === 'info' ? 'ℹ️' : '🚫';
    t.innerHTML = `<div class="ico">${icon}</div>
                   <div class="body"><div class="title">${title}</div>${desc?`<div class="desc">${desc}</div>`:''}</div>
                   <button class="close" aria-label="Close">✕</button>`;
    host.appendChild(t);
    const dismiss = () => { t.classList.add('out'); setTimeout(()=>t.remove(),260); };
    t.querySelector('.close').onclick = dismiss;
    setTimeout(dismiss, 6000);
  };

  // Auto-show on pages flagged with ?unauthorized=1
  try {
    const u = new URL(window.location.href);
    if (u.searchParams.get('unauthorized') === '1') {
      window.LV.toast('Unauthorized action blocked',
        "You don't have permission to do that. The action was safely cancelled — nothing was changed.",
        'danger');
      u.searchParams.delete('unauthorized');
      window.history.replaceState({}, '', u.toString());
    }
  } catch(_){}
})();

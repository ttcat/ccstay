/* Desk Mates: every session is a round mate in its own colour; the whole crowd sits on a bench at the top,
   waiting ones first. Tap one on the bench to jump to its row. */
ccstayTheme({
  render: function (c) {
    var esc = c.esc, t = c.t, D = c.data;
    // [body, darker accent] pairs; the core picks which one a session is
    var PAL = [
      ['#8FE3C2', '#2E8C68'], ['#FFB48A', '#C0603A'], ['#C9B6FF', '#6F56B8'], ['#8FCBFF', '#2F7AB8'],
      ['#FFE27A', '#B59420'], ['#FF9EC4', '#C04C80'], ['#FF9A8A', '#C04A3A'], ['#B8DFA0', '#5F9448'],
      ['#D9C5F5', '#7D5FBF'], ['#8FE0E8', '#2A8E99'], ['#FFEFA8', '#B8A030'], ['#FFC3D6', '#C96A8A'],
      ['#FFC08A', '#C27830'], ['#8FD9C8', '#2B8C78'], ['#B5C1FF', '#5A68C2'], ['#E2B4D4', '#9A5A88'],
      ['#FFD1A8', '#C08048'], ['#D4E8A0', '#7E9A38'], ['#C9E6FF', '#4A86C0'], ['#D8A9E8', '#8A4FA0'],
      ['#EAD8B0', '#9C8048'], ['#FFAAB5', '#C04555'], ['#A8F0D8', '#3A9A78'], ['#A9B8D8', '#56688F']
    ];
    var pick = c.assign(PAL.length);
    var INK = '#2A2740';

    function mate(s, size) {
      var p = PAL[pick(s)], col = p[0], d = p[1], st = s.state, face, extra = '';
      if (st === 'working') {
        face = '<ellipse cx="15.5" cy="22.5" rx="1.7" ry="2.1" fill="' + INK + '"/><ellipse cx="24.5" cy="22.5" rx="1.7" ry="2.1" fill="' + INK + '"/><path d="M18.2 27.2q1.8 1.2 3.6 0" stroke="' + INK + '" stroke-width="1.2" fill="none" stroke-linecap="round"/>';
        extra = '<rect x="10" y="29.5" width="20" height="8" rx="2" fill="#3A3858"/><rect x="12" y="31" width="16" height="4.5" rx="1" fill="#A9C8FF"/><circle class="h1" cx="12.5" cy="30" r="2.3" fill="' + d + '"/><circle class="h2" cx="27.5" cy="30" r="2.3" fill="' + d + '"/>';
      } else if (st === 'waiting') {
        face = '<circle cx="15.5" cy="22" r="2.7" fill="' + INK + '"/><circle cx="24.5" cy="22" r="2.7" fill="' + INK + '"/><circle cx="16.4" cy="21" r=".9" fill="#fff"/><circle cx="25.4" cy="21" r=".9" fill="#fff"/><circle cx="20" cy="27.5" r="1.5" fill="' + INK + '"/><path d="M12.5 17.5q2-1.6 4.5-.8M23 16.7q2.5-.8 4.5.8" stroke="' + INK + '" stroke-width="1.2" fill="none" stroke-linecap="round"/>';
        extra = '<path d="M31 26L35 14" stroke="' + d + '" stroke-width="3.2" stroke-linecap="round"/><circle cx="35.3" cy="13" r="2.6" fill="' + d + '"/>' +
          '<rect x="22" y="-1" width="15" height="12" rx="6" fill="#FF7A59"/><path d="M26 10.5L24.5 14L29 11" fill="#FF7A59"/><text x="29.5" y="8.6" font-size="9.5" font-weight="700" fill="#fff" text-anchor="middle" font-family="Fredoka,system-ui">!</text>';
      } else if (st === 'idle') {
        face = '<circle cx="16.5" cy="22.3" r="2" fill="' + INK + '"/><circle cx="25.5" cy="22.3" r="2" fill="' + INK + '"/><circle cx="17.3" cy="21.5" r=".7" fill="#fff"/><circle cx="26.3" cy="21.5" r=".7" fill="#fff"/><path d="M19.5 27q1.8 1.4 3.6 0" stroke="' + INK + '" stroke-width="1.2" fill="none" stroke-linecap="round"/>';
        extra = '<rect x="31" y="27" width="7" height="7" rx="1.5" fill="#fff" stroke="' + d + '" stroke-width="1.2"/><path d="M38 29.5q2.5 0 2.5 1.8T38 33" fill="none" stroke="' + d + '" stroke-width="1.2"/><path d="M33.5 24.5q1-1.5 0-3M36 24.5q1-1.5 0-3" stroke="' + d + '" stroke-width="1" fill="none" opacity=".7" stroke-linecap="round"/>';
      } else {
        face = '<path d="M13 22.5q2.5 2.4 5 0M22 22.5q2.5 2.4 5 0" stroke="' + INK + '" stroke-width="1.5" fill="none" stroke-linecap="round"/><path d="M19 27.2h2" stroke="' + INK + '" stroke-width="1.2" stroke-linecap="round"/>';
        extra = '<text class="z1" x="30" y="15" font-size="9" font-weight="700" fill="' + d + '" font-family="Fredoka,system-ui">z</text><text class="z2" x="35" y="9" font-size="7.5" font-weight="700" fill="' + d + '" font-family="Fredoka,system-ui">z</text>';
      }
      var body = '<g class="b"><ellipse cx="20" cy="37.5" rx="12" ry="1.8" fill="#000" opacity=".08"/><ellipse cx="20" cy="24" rx="15" ry="13.5" fill="' + col + '"/><ellipse cx="14" cy="16.5" rx="4" ry="2.2" fill="#fff" opacity=".35"/>' + face +
        '<circle cx="11.5" cy="26.5" r="1.9" fill="#FF7A9B" opacity=".45"/><circle cx="28.5" cy="26.5" r="1.9" fill="#FF7A9B" opacity=".45"/></g>';
      return '<svg class="m ' + st + '" viewBox="0 0 40 40" width="' + size + '" height="' + size + '" aria-hidden="true"' + (st === 'asleep' ? ' style="filter:saturate(.6) brightness(.95)"' : '') + '>' + body + extra + '</svg>';
    }

    var ALL = [];
    D.folders.forEach(function (f) { f.sessions.forEach(function (s) { ALL.push(s); }); });
    var ORDER = {waiting: 0, working: 1, idle: 2, asleep: 3};
    function bench() {
      if (!ALL.length) return '';
      var sorted = ALL.map(function (s, i) { return {s: s, i: i}; }).sort(function (a, b) { return ORDER[a.s.state] - ORDER[b.s.state] || a.i - b.i; });
      var W = 358, n = sorted.length, step = Math.min(26, (W - 20) / n), x0 = (W - step * (n - 1)) / 2;
      var out = '<svg class="bench" viewBox="0 0 ' + W + ' 74" role="img" aria-label="' + esc(c.lang === 'zh' ? '大家坐在長椅上，等你回覆的排前面' : 'Everyone on the bench, waiting first') + '">' +
        '<rect x="6" y="40" width="' + (W - 12) + '" height="16" rx="8" fill="var(--bench)"/><rect x="6" y="54" width="' + (W - 12) + '" height="7" rx="3.5" fill="var(--bench-dk)"/>' +
        '<rect x="22" y="60" width="6" height="12" rx="3" fill="var(--bench-dk)"/><rect x="' + (W - 28) + '" y="60" width="6" height="12" rx="3" fill="var(--bench-dk)"/>';
      sorted.forEach(function (e, i) {
        var x = x0 + i * step - 13, y = e.s.state === 'waiting' ? 8 : 18;
        out += '<g class="jump" data-go="' + esc(e.s.key) + '" transform="translate(' + x.toFixed(1) + ' ' + y + ')"><title>' + esc(e.s.title) + '</title>' + mate(e.s, 26) + '</g>';
      });
      return out + '</svg>';
    }
    function dot(f) { // the folder dot follows its first session's colour
      return f.sessions.length ? PAL[pick(f.sessions[0])][0] : 'var(--line)';
    }

    var h = '<header><div class="hd"><h1>' + t.title + '</h1>' + c.switcher + '</div><p class="meta">' + c.summary + '<br>' + c.generated + '</p></header>' + bench() + c.chips;
    if (c.empty) h += '<p class="empty">' + c.empty + '</p>';
    D.folders.forEach(function (f) {
      h += '<div class="grp" data-grp><div class="gh"><i class="dot" style="background:' + dot(f) + '"></i>' + esc(f.head) + '<span>' + esc(f.label) + '</span></div>';
      f.sessions.forEach(function (s) {
        var inner = '<span aria-hidden="true">' + mate(s, 42) + '</span><div><div class="t">' + esc(s.title) + '</div>' + (s.sub ? '<div class="s">' + esc(s.sub) + '</div>' : '') +
          '<span class="sr">' + t.state[s.state] + '</span></div><div class="tm">' + (s.state === 'waiting' ? '<b>' + t.needsYou + '</b>' : '') + esc(s.when) + '</div>';
        h += s.url ? '<a class="row" data-st="' + s.state + '" data-key="' + esc(s.key) + '" href="' + esc(s.url) + '" target="_blank" rel="noopener">' + inner + '</a>'
                   : '<div class="row" data-st="' + s.state + '" data-key="' + esc(s.key) + '">' + inner + '</div>';
      });
      h += '</div>';
    });
    h += '<p class="empty" data-empty hidden>' + t.emptyFilter + '</p>';
    if (D.closed.length) {
      h += '<section data-closed><h2>' + t.closed + '</h2><p class="hint">' + t.closedHint + '</p><div class="grp closed">';
      D.closed.forEach(function (x) {
        h += '<button type="button" class="row" data-copy="' + esc(x.cmd) + '" aria-label="' + esc(t.copyLabel(x.title)) + '"><div><div class="t">' + esc(x.title) + '</div>' +
          (x.prompt ? '<div class="s">' + esc(x.prompt) + '</div>' : '') + '<div class="s">' + esc(x.cwd) + ' · ' + esc(x.when) + '</div></div><span class="cp">' + t.copy + '</span></button>';
      });
      h += '</div></section>';
    }
    return h;
  },
  mount: function (root) {
    root.querySelectorAll('.bench .jump').forEach(function (g) {
      g.addEventListener('click', function () {
        var key = g.getAttribute('data-go'), row = null;
        root.querySelectorAll('.row[data-key]').forEach(function (r) { if (r.getAttribute('data-key') === key) row = r; });
        if (!row) return;
        row.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center'});
        row.classList.remove('flash'); void row.offsetWidth; row.classList.add('flash');
      });
    });
  }
});

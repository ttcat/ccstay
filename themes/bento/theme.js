/* Bento: each folder is a compartment, each session a small food with a face.
   The face sits at (fx, fy) in a 48x48 box; the core picks which food a session is. */
ccstayTheme({
  render: function (c) {
    var esc = c.esc, t = c.t, D = c.data;
    var FOODS = [
      // onigiri
      {fy: 22, s: '<path d="M24 7c6 0 17 15 17 24 0 6-7 9-17 9S7 37 7 31C7 22 18 7 24 7z" fill="#FFFDF8" stroke="#E6DFD2" stroke-width="1.5"/><rect x="16" y="29" width="16" height="11" rx="2.5" fill="#2F3D33"/>'},
      // tamagoyaki
      {fy: 26, s: '<rect x="7" y="13" width="34" height="24" rx="8" fill="#FFD36B"/><path d="M11 19.5h26M11 32h26" stroke="#F0B64A" stroke-width="1.5" opacity=".7"/><rect x="11" y="16" width="10" height="4" rx="2" fill="#fff" opacity=".45"/>'},
      // octopus sausage
      {fy: 22, s: '<rect x="14" y="30" width="4" height="10" rx="2" fill="#E8564A"/><rect x="21" y="31" width="4" height="10" rx="2" fill="#E8564A"/><rect x="28" y="31" width="4" height="10" rx="2" fill="#E8564A"/><rect x="34" y="29" width="4" height="9" rx="2" fill="#E8564A" transform="rotate(-18 36 29)"/><rect x="10" y="29" width="4" height="9" rx="2" fill="#E8564A" transform="rotate(18 12 29)"/><ellipse cx="24" cy="21" rx="14" ry="12" fill="#F26B5B"/><ellipse cx="18" cy="14" rx="4" ry="2" fill="#fff" opacity=".35"/>'},
      // broccoli
      {fy: 25, s: '<rect x="20" y="28" width="8" height="12" rx="3" fill="#C9E8A8"/><circle cx="15" cy="23" r="8" fill="#6DBA6A"/><circle cx="33" cy="23" r="8" fill="#6DBA6A"/><circle cx="24" cy="17" r="9" fill="#7CC97A"/><circle cx="24" cy="25" r="8.5" fill="#86D183"/><circle cx="19" cy="14" r="2" fill="#fff" opacity=".3"/>'},
      // tomato
      {fy: 28, s: '<circle cx="24" cy="27" r="14" fill="#FF6B6B"/><path d="M24 12l-5-4 1.5 5.5-6 .5 5 3 3.5 1.5 3.5-1.5 5-3-6-.5L29 8z" fill="#5FB36A"/><ellipse cx="17.5" cy="21" rx="3.5" ry="2" fill="#fff" opacity=".35"/>'},
      // gyoza
      {fy: 31, ink: '#5C4530', s: '<path d="M6 32c0-10 8-18 18-18s18 8 18 18z" fill="#F7E8CC" stroke="#E7D2AC" stroke-width="1.5"/><path d="M12 20l2 6M17 16.5l1.5 6M24 15v6M31 16.5l-1.5 6M36 20l-2 6" stroke="#E7D2AC" stroke-width="1.6" stroke-linecap="round"/><rect x="6" y="31" width="36" height="7" rx="3.5" fill="#F2DDB7"/>'},
      // strawberry
      {fy: 26, s: '<path d="M24 42C14 36 8 28 8 20a9 9 0 0 1 16-5.5A9 9 0 0 1 40 20c0 8-6 16-16 22z" fill="#F4536E"/><path d="M24 10l-6-3 3 4-5 .5 4.5 2.5-1 4 4.5-3 4.5 3-1-4 4.5-2.5-5-.5 3-4z" fill="#5FB36A"/><g fill="#FFD1DA" opacity=".9"><circle cx="17" cy="21" r="1"/><circle cx="31" cy="21" r="1"/><circle cx="24" cy="33" r="1"/><circle cx="19" cy="31" r="1"/><circle cx="29" cy="31" r="1"/><circle cx="22" cy="37" r="1"/><circle cx="26" cy="37" r="1"/></g>'},
      // ebi fry
      {fx: 28, fy: 27, s: '<path d="M12 24l-9-8 1 7-5 3 8 3z" fill="#E8564A"/><path d="M11 24l-5-4 .5 4z" fill="#F58A7C"/><path d="M9 27c0-6 8-10 16-11 9-1 19 3 19 11 0 7-9 11-18 11S9 34 9 27z" fill="#E9A84A"/><g fill="#FBE0A8" opacity=".9"><circle cx="15" cy="23" r="1.2"/><circle cx="21" cy="19.5" r="1.1"/><circle cx="30" cy="18.5" r="1.2"/><circle cx="39" cy="24" r="1.1"/><circle cx="16" cy="32" r="1.1"/><circle cx="36" cy="34" r="1.2"/></g><g fill="#C9802A" opacity=".6"><circle cx="19" cy="34" r="1"/><circle cx="26" cy="37" r="1"/><circle cx="41" cy="31" r="1"/></g>'},
      // salmon nigiri
      {fy: 21, s: '<path d="M8 33c0-5 7-8 16-8s16 3 16 8-7 7-16 7S8 38 8 33z" fill="#FFFDF8" stroke="#E6DFD2" stroke-width="1.5"/><path d="M6 25c2-7 10-11 18-11s16 4 18 11c-4 3-10 4-18 4S10 28 6 25z" fill="#FF9D6E"/><path d="M11.5 19q3 3 1.5 8M36.5 19q-3 3-1.5 8" stroke="#FFD3BC" stroke-width="1.8" fill="none" stroke-linecap="round" opacity=".85"/>'},
      // maki roll
      {fy: 23, s: '<circle cx="24" cy="26" r="15" fill="#2F3D33"/><circle cx="24" cy="26" r="11.5" fill="#FFFDF8"/><circle cx="20" cy="32.5" r="2.6" fill="#F26B5B"/><circle cx="26.5" cy="33.5" r="2.4" fill="#7CC97A"/><circle cx="29.5" cy="30" r="2" fill="#FFD36B"/>'},
      // edamame
      {fy: 26, s: '<path d="M5 28l-2-4" stroke="#4E8F3F" stroke-width="2" stroke-linecap="round"/><path d="M5 28c4-9 11-14 19-14s15 5 19 14c-5 5-12 7-19 7S10 33 5 28z" fill="#7BC46B"/><circle cx="13" cy="27" r="5" fill="#8ED07E" opacity=".7"/><circle cx="35" cy="27" r="5" fill="#8ED07E" opacity=".7"/><ellipse cx="14" cy="20" rx="4" ry="1.8" fill="#fff" opacity=".3"/>'},
      // purin
      {fy: 29, s: '<ellipse cx="24" cy="38" rx="17" ry="3" fill="#FFFDF8" stroke="#E6DFD2" stroke-width="1.2"/><path d="M10 36l2.5-17h23L38 36c-4 2-10 3-14 3s-10-1-14-3z" fill="#FFD36B"/><path d="M12.5 19c0-3 5-5 11.5-5s11.5 2 11.5 5c0 2-2 3-4 4l-1.5 4-2-3.5c-1 .5-3 .7-4 .7s-3-.2-4-.7l-2 3.5-1.5-4c-2-1-4-2-4-4z" fill="#8A4B1E"/>'},
      // takoyaki
      {fy: 30, s: '<path d="M16 16L10 6" stroke="#E7D2AC" stroke-width="2" stroke-linecap="round"/><circle cx="24" cy="26" r="13" fill="#B97A42"/><path d="M11.5 24a12.5 12.5 0 0 1 25 0c-4 3-21 3-25 0z" fill="#8A5327"/><path d="M15 20l3 3 3-3 3 3 3-3 3 3 3-3" stroke="#FFF4DC" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/><g fill="#8FBF6A"><circle cx="19" cy="15.5" r="1"/><circle cx="29" cy="15" r="1"/></g>'},
      // sakura mochi
      {fy: 27, s: '<path d="M8 30c0-9 7-15 16-15s16 6 16 15c0 6-7 9-16 9S8 36 8 30z" fill="#F7B7C8"/><ellipse cx="16" cy="21" rx="4" ry="2" fill="#fff" opacity=".4"/><path d="M5 34c6 5 32 5 38 0-3 4-8 6-19 6S8 38 5 34z" fill="#6FA85A"/><path d="M9 36.5q15 2.5 30 0" stroke="#4E8F3F" stroke-width="1.2" fill="none" opacity=".7"/>'},
      // dango
      {fy: 25, s: '<rect x="1" y="25" width="46" height="2.4" rx="1.2" fill="#C9A275"/><circle cx="9" cy="26" r="8" fill="#F7A8B8"/><circle cx="39" cy="26" r="8" fill="#A9D68B"/><circle cx="24" cy="26" r="8.5" fill="#FFFDF8" stroke="#E6DFD2" stroke-width="1.2"/><circle cx="6.5" cy="23" r="1.6" fill="#fff" opacity=".5"/><circle cx="36.5" cy="23" r="1.6" fill="#fff" opacity=".5"/>'},
      // boiled egg
      {fy: 26, s: '<ellipse cx="24" cy="26" rx="16" ry="13.5" fill="#FFFDF8" stroke="#E6DFD2" stroke-width="1.5"/><circle cx="24" cy="27" r="9.5" fill="#FFC436"/><ellipse cx="20" cy="22" rx="2.5" ry="1.3" fill="#fff" opacity=".55"/>'},
      // carrot flower
      {fy: 26, s: '<g fill="#FF9A4D"><circle cx="24" cy="17.5" r="6.5"/><circle cx="32.1" cy="23.4" r="6.5"/><circle cx="29" cy="32.9" r="6.5"/><circle cx="19" cy="32.9" r="6.5"/><circle cx="15.9" cy="23.4" r="6.5"/></g><circle cx="24" cy="26" r="9" fill="#FFA85F"/><ellipse cx="20" cy="21" rx="2.5" ry="1.3" fill="#fff" opacity=".4"/>'},
      // lemon slice
      {fy: 26, s: '<circle cx="24" cy="26" r="14.5" fill="#FFD84A"/><circle cx="24" cy="26" r="12" fill="#FFF3B0"/><g stroke="#FFD84A" stroke-width="1.6" stroke-linecap="round">' +
        [0, 45, 90, 135, 180, 225, 270, 315].map(function (a) { var r = a * Math.PI / 180, c1 = Math.cos(r), s1 = Math.sin(r); return '<path d="M' + (24 + 8.5 * c1).toFixed(1) + ' ' + (26 + 8.5 * s1).toFixed(1) + 'L' + (24 + 11.5 * c1).toFixed(1) + ' ' + (26 + 11.5 * s1).toFixed(1) + '"/>'; }).join('') + '</g>'},
      // peach
      {fy: 27, s: '<path d="M26 13c3-5 8-5 10-4-1 4-5 6-10 4z" fill="#6FA85A"/><path d="M24 41c-9 0-16-6-16-15 0-6 4-11 9-11 3 0 5 1 7 3 2-2 4-3 7-3 5 0 9 5 9 11 0 9-7 15-16 15z" fill="#FFB199"/><path d="M24 18c2-2 4-3 7-3 5 0 9 5 9 11 0 9-7 15-16 15z" fill="#FF8FA3" opacity=".5"/><path d="M24 15.5q-1.5 3.5 0 7" stroke="#E8788C" stroke-width="1.2" fill="none" opacity=".6" stroke-linecap="round"/><ellipse cx="16" cy="21" rx="3" ry="1.6" fill="#fff" opacity=".4"/>'},
      // shiitake
      {fy: 23, ink: '#2A1A10', s: '<rect x="18" y="29" width="12" height="11" rx="4" fill="#F0E2CC"/><path d="M5 27c0-9 9-16 19-16s19 7 19 16c0 2-1 3-3 3H8c-2 0-3-1-3-3z" fill="#A86E42"/><g fill="#F0DFC8" opacity=".75"><circle cx="16" cy="17.5" r="1.7"/><circle cx="29" cy="14.5" r="1.4"/><circle cx="37" cy="21" r="1.3"/></g>'},
      // kamaboko
      {fy: 25, s: '<rect x="5" y="32" width="38" height="5" rx="1.5" fill="#D9B07A"/><path d="M8 32a16 16 0 0 1 32 0z" fill="#FFFDF8"/><path d="M8 32a16 16 0 0 1 32 0" fill="none" stroke="#F6A1B8" stroke-width="4"/><path d="M13 23q4-5 9-5" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round" opacity=".7"/>'},
      // apple rabbit
      {fy: 30, s: '<path d="M13 26l2-13 6 11z" fill="#E84A5F"/><path d="M27 24l6-11 2 13z" fill="#E84A5F"/><path d="M15.5 23l1-7 2.5 5z" fill="#FF8A99"/><path d="M29 22l3-6 .8 7z" fill="#FF8A99"/><path d="M7 31c0-6 8-9 17-9s17 3 17 9-8 10-17 10S7 37 7 31z" fill="#FFF6E6"/><path d="M8 29c4-5 10-7 16-7s12 2 16 7" stroke="#E84A5F" stroke-width="3" fill="none" stroke-linecap="round"/>'},
      // watermelon
      {fy: 23, s: '<path d="M6 17h36L24 41z" fill="#FF6B6B"/><path d="M5 15h38v5H5z" fill="#5FB36A"/><path d="M6 20h36v2H6z" fill="#F4FFE8" opacity=".9"/><g fill="#2F2A26"><ellipse cx="14" cy="23.5" rx="1.1" ry="1.7"/><ellipse cx="34" cy="23.5" rx="1.1" ry="1.7"/><ellipse cx="24" cy="33.5" rx="1.1" ry="1.7"/></g>'},
      // baozi
      {fy: 28, s: '<path d="M7 31c0-11 8-18 17-18s17 7 17 18c0 5-8 8-17 8S7 36 7 31z" fill="#FFF8EE" stroke="#EADFD0" stroke-width="1.5"/><path d="M24 14q-4 2-7 6M24 14q4 2 7 6M24 14q-1 3-2 6M24 14q1 3 2 6M24 14q-7 0-11 3M24 14q7 0 11 3" stroke="#E6D6C0" stroke-width="1.4" fill="none" stroke-linecap="round"/><circle cx="24" cy="14" r="2" fill="#EADFD0"/>'}
    ];
    var pick = c.assign(FOODS.length);

    function food(s) {
      var f = FOODS[pick(s)], st = s.state, fx = f.fx || 24, fy = f.fy, ink = f.ink || '#3B2A1C', face, extra = '';
      if (st === 'asleep') face = '<path d="M' + (fx - 7) + ' ' + fy + 'q2.5 2.3 5 0M' + (fx + 2) + ' ' + fy + 'q2.5 2.3 5 0" stroke="' + ink + '" stroke-width="1.5" fill="none" stroke-linecap="round"/>';
      else if (st === 'waiting') face = '<circle cx="' + (fx - 4.5) + '" cy="' + fy + '" r="2.4" fill="' + ink + '"/><circle cx="' + (fx + 4.5) + '" cy="' + fy + '" r="2.4" fill="' + ink + '"/><circle cx="' + (fx - 3.7) + '" cy="' + (fy - .9) + '" r=".8" fill="#fff"/><circle cx="' + (fx + 5.3) + '" cy="' + (fy - .9) + '" r=".8" fill="#fff"/><circle cx="' + fx + '" cy="' + (fy + 5) + '" r="1.5" fill="' + ink + '"/><path d="M' + (fx + 11) + ' ' + (fy - 9) + 'q-3 4 0 6.5q3-2.5 0-6.5z" fill="#7CC4FF"/>';
      else if (st === 'working') face = '<ellipse cx="' + (fx - 4.5) + '" cy="' + fy + '" rx="1.6" ry="2" fill="' + ink + '"/><ellipse cx="' + (fx + 4.5) + '" cy="' + fy + '" rx="1.6" ry="2" fill="' + ink + '"/><path d="M' + (fx - 2) + ' ' + (fy + 4.5) + 'q2 1.3 4 0" stroke="' + ink + '" stroke-width="1.2" fill="none" stroke-linecap="round"/>';
      else face = '<circle cx="' + (fx - 4.5) + '" cy="' + fy + '" r="1.8" fill="' + ink + '"/><circle cx="' + (fx + 4.5) + '" cy="' + fy + '" r="1.8" fill="' + ink + '"/><path d="M' + (fx - 1.5) + ' ' + (fy + 4.5) + 'h3" stroke="' + ink + '" stroke-width="1.2" stroke-linecap="round"/>';
      face += '<circle cx="' + (fx - 8.5) + '" cy="' + (fy + 3.5) + '" r="1.8" fill="#FF7A9B" opacity=".4"/><circle cx="' + (fx + 8.5) + '" cy="' + (fy + 3.5) + '" r="1.8" fill="#FF7A9B" opacity=".4"/>';
      if (st === 'working') extra = '<g stroke="var(--mute)" stroke-width="1.6" fill="none" stroke-linecap="round"><path class="s1" d="M17 9c-1.5-2 1.5-3 0-5"/><path class="s2" d="M24 7c-1.5-2 1.5-3 0-5"/><path class="s3" d="M31 9c-1.5-2 1.5-3 0-5"/></g>';
      else if (st === 'waiting') extra = '<g class="fl"><path d="M38 34L41 7" stroke="#B88A5E" stroke-width="2" stroke-linecap="round"/><path d="M41 7l-11 3.5L41 15z" fill="var(--need)"/><text x="37.2" y="13.6" font-size="6.5" font-weight="900" fill="#fff" text-anchor="middle" font-family="\'Baloo 2\',system-ui">!</text></g>';
      else if (st === 'asleep') extra = '<text class="z1" x="37" y="14" font-size="9" font-weight="700" fill="var(--mute)" font-family="\'Baloo 2\',system-ui">z</text><text class="z2" x="42" y="7" font-size="7" font-weight="700" fill="var(--mute)" font-family="\'Baloo 2\',system-ui">z</text>';
      return '<svg class="f ' + st + '" viewBox="0 0 48 48" aria-hidden="true"><ellipse cx="24" cy="43.5" rx="12" ry="1.6" fill="#000" opacity=".09"/><g class="bd">' + f.s + face + '</g>' + extra + '</svg>';
    }

    var h = '<header><div class="hd"><h1>' + t.title + '</h1>' + c.switcher + '</div><p class="meta">' + c.summary + '<br>' + c.generated + '</p></header>' + c.chips;
    h += '<div class="box">';
    if (c.empty) h += '<p class="empty">' + c.empty + '</p>';
    // pack compartments into rows of 3 units, keeping recency order as far as the row allows
    var pending = D.folders.map(function (f) { return {f: f, n: Math.min(3, f.sessions.length)}; }), room = 3;
    while (pending.length) {
      var k = -1;
      for (var i = 0; i < pending.length; i++) if (pending[i].n <= room) { k = i; break; }
      if (k < 0) { room = 3; k = 0; }
      var p = pending.splice(k, 1)[0], f = p.f;
      room -= p.n; if (room <= 0) room = 3;
      var need = f.sessions.some(function (s) { return s.state === 'waiting'; });
      h += '<div class="cell' + (need ? ' need' : '') + '" data-grp style="--n:' + p.n + '"><span class="tag">' + esc(f.label) + '</span>';
      f.sessions.forEach(function (s) {
        var inner = food(s) + '<div class="t">' + esc(s.title) + '</div>' + (s.sub ? '<div class="s">' + esc(s.sub) + '</div>' : '') +
          '<div class="tm">' + (s.state === 'waiting' ? t.needsYou + ' · ' : '') + esc(s.when) + '</div><span class="sr">' + t.state[s.state] + '</span>';
        h += s.url ? '<a class="tile" data-st="' + s.state + '" href="' + esc(s.url) + '" target="_blank" rel="noopener">' + inner + '</a>'
                   : '<div class="tile" data-st="' + s.state + '">' + inner + '</div>';
      });
      h += '</div>';
    }
    h += '<p class="empty" data-empty hidden>' + t.emptyFilter + '</p></div>';
    if (D.closed.length) {
      h += '<section data-closed><h2>' + t.closed + '</h2><p class="hint">' + t.closedHint + '</p><div class="tray">';
      D.closed.forEach(function (x) {
        h += '<button type="button" class="crow" data-copy="' + esc(x.cmd) + '" aria-label="' + esc(t.copyLabel(x.title)) + '"><div><div class="t">' + esc(x.title) + '</div>' +
          (x.prompt ? '<div class="s">' + esc(x.prompt) + '</div>' : '') + '<div class="s">' + esc(x.cwd) + ' · ' + esc(x.when) + '</div></div><span class="cp">' + t.copy + '</span></button>';
      });
      h += '</div></section>';
    }
    return h;
  }
});

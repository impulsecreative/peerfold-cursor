# Module patterns

These patterns worked on live migrations. Replace the `ex-` prefix, colors and fonts with values from `tokens.md`. Colors below come from the example site.

A module has four parts: `fields` (JSON), `html` (template with `{{field}}`, `<pf-if>`, `<pf-each>`), `css` and an optional `script`. Send large parts as files, for example `"css": "$file:/path/mod/ex-hero.css"`.

## Hero with photo, overlay and web fonts
Use for a photo hero with a color wash, an uppercase display font and colored accent words.

Fields: `bg` (image), `title` (text), `sub` (list of `t` text, `y` boolean for accent color, `b` bold, `br` new line), `cta_label`, `cta_url`.

HTML (short form):
```html
<section class="ex-h"><div class="ex-h-in">
  <h1 class="ex-h-t">{{title}}</h1>
  <p class="ex-h-s"><pf-each field="sub" as="r" limit="20"><pf-if field="r.br"><span class="ex-h-br"></span></pf-if><pf-if field="r.y"><span class="ex-h-y">{{r.t}}</span><pf-else>{{r.t}}</pf-else></pf-if></pf-each></p>
  <pf-if field="cta_label"><a class="ex-h-btn" href="{{cta_url}}">{{cta_label}}</a></pf-if>
</div></section>
```

CSS:
```css
.ex-h{position:relative;overflow:hidden;background-color:#0f3663;background-size:cover;background-position:50% 50%}
.ex-h-in{position:relative;max-width:1180px;margin:0 auto;padding:110px 20px 140px}
.ex-h-t{font-family:"Changa One",Impact,sans-serif;font-size:74px;line-height:80px;text-transform:uppercase;color:#ffffff;margin:0 0 30px}
.ex-h-s{font-family:"Open Sans",sans-serif;font-style:italic;font-size:30px;line-height:40px;color:#ffffff;margin:0 0 50px}
.ex-h-y{color:#ffcc00}
.ex-h-br{display:block}
.ex-h-btn{display:inline-block;background:#ffcc00;color:#0f3663;font-size:18px;text-transform:uppercase;text-decoration:none;padding:13px 24px;border-radius:5px;transition:background-color .2s ease,transform .2s ease}
.ex-h-btn:hover{background:#f2c200;transform:translateY(-1px)}
@media (max-width:767px){.ex-h-in{padding:70px 20px 90px}.ex-h-t{font-size:44px;line-height:50px}.ex-h-s{font-size:22px;line-height:32px}}
```

Script: sets the photo with the wash (the template cannot bind a background image) and loads real web fonts once per page.
```js
export default function(root, fields){
  var s = root.querySelector('section') || root;
  if (fields.bg) s.style.backgroundImage = 'linear-gradient(rgba(15,54,99,.84),rgba(15,54,99,.84)),url("' + fields.bg + '")';
  var d = root.ownerDocument; if (!d.fonts || d.__exFonts) return; d.__exFonts = true;
  [['Changa One', 'https://fonts.gstatic.com/s/changaone/<file>.woff2', {weight:'400 700'}]]
    .forEach(function(f){ try { new FontFace(f[0], 'url(' + f[1] + ') format("woff2")', f[2]).load()
      .then(function(x){ d.fonts.add(x); }).catch(function(){}); } catch(e){} });
}
```
Get the woff2 URLs from the source `fonts.json` or the Google Fonts CSS.

Note: the h1 in this module is real, but the checklist cannot see it. Record the `seo.heading.main` warning as a known false warning.

## Top utility bar (above the header)
The layout does not take a top-level module. Put the module inside `sites/footer`. Its script moves it above the header.

HTML:
```html
<div class="ex-tb"><div class="ex-tb-in"><pf-each field="links" as="l" limit="4"><a class="ex-tb-a" href="{{l.url}}">{{l.label}}</a></pf-each></div></div>
```
CSS:
```css
.ex-tb{background:#0f3663;font-size:14px;line-height:20px}
.ex-tb-in{max-width:940px;margin:0 auto;padding:0 20px;display:flex;justify-content:flex-end}
.ex-tb-a{display:block;padding:10px 20px;color:#ffcc00;text-decoration:none}
.ex-tb-a:hover{text-decoration:underline}
@media (max-width:767px){.ex-tb-in{justify-content:center}.ex-tb-a{padding:8px 10px}}
```
Script (also restyles the native header CTA):
```js
export default function(root){
  var d = root.ownerDocument, hdr = d.querySelector('.pf-hdr');
  if (hdr) { var top = hdr;
    while (top.parentElement && top.parentElement !== d.body && !top.parentElement.contains(root)) top = top.parentElement;
    if (top.parentElement) top.parentElement.insertBefore(root, top); }
  if (d.__exCta) return; d.__exCta = true;
  var st = d.createElement('style');
  st.textContent = '.pf-hdr .pf-hdr-cta{background:#ffcc00!important;color:#0f3663!important;border-color:#ffcc00!important}';
  d.head.appendChild(st);
}
```
If the CSP blocks the injected style, set `style` on `.pf-hdr-cta` from the script.

## Accessible testimonial slider
Turns a static quote list into a slider. Without the script the list stays readable.

Fields: `heading`, `heading_hl` (italic accent part), `heading_after`, `autoplay` (boolean, default off), `items` (list of `quote`, `name`).

HTML:
```html
<section class="ex-q"><div class="ex-q-in">
  <h2 class="ex-q-h">{{heading}} <em>{{heading_hl}}</em> {{heading_after}}</h2>
  <div class="ex-q-track"><pf-each field="items" as="q" limit="24"><figure class="ex-q-q">
    <blockquote class="ex-q-bq"><p>{{q.quote}}</p></blockquote><figcaption class="ex-q-n">{{q.name}}</figcaption>
  </figure></pf-each></div>
  <div class="ex-q-nav"><button type="button" class="ex-q-prev" aria-label="Previous testimonial">&lsaquo;</button><div class="ex-q-dots"></div><button type="button" class="ex-q-next" aria-label="Next testimonial">&rsaquo;</button></div>
</div></section>
```
CSS (slider part):
```css
.ex-q-track{position:relative;touch-action:pan-y}
.ex-q-on .ex-q-q{display:none;margin:0}
.ex-q-on .ex-q-q.ex-q-cur{display:block;animation:exqf .5s ease}
@keyframes exqf{from{opacity:0}to{opacity:1}}
@media (prefers-reduced-motion:reduce){.ex-q-on .ex-q-q.ex-q-cur{animation:none}}
.ex-q-nav{display:none;align-items:center;justify-content:center;gap:18px;margin-top:26px}
.ex-q-on .ex-q-nav{display:flex}
.ex-q-prev,.ex-q-next{width:44px;height:44px;border-radius:50%;border:2px solid #ffffff;background:transparent;color:#ffffff;font-size:28px;cursor:pointer;padding:0}
.ex-q-prev:focus-visible,.ex-q-next:focus-visible,.ex-q-dot:focus-visible{outline:3px solid #ffcc00;outline-offset:2px}
.ex-q-dots{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.ex-q-dot{width:12px;height:12px;border-radius:50%;border:0;background:rgba(255,255,255,.5);padding:0;cursor:pointer}
.ex-q-dot[aria-current="true"]{background:#ffcc00}
```
The dots are 12px. Add padding or a larger hit area if you need 24px targets.

Script:
```js
export default function(root, fields){
  var s = root.querySelector('section') || root, tr = root.querySelector('[class$="ex-q-track"]');
  tr.setAttribute('aria-live', 'polite'); s.setAttribute('aria-roledescription', 'carousel'); s.setAttribute('aria-label', 'Testimonials');
  var qs = [].slice.call(tr.querySelectorAll('figure')); if (qs.length < 2) return;
  var cls = function(el, suf){ var c = [].slice.call(el.classList).find(function(x){ return /ex-q-q$/.test(x); }); return c ? c.replace(/ex-q-q$/, suf) : suf; };
  var CUR = cls(qs[0], 'ex-q-cur'), ON = cls(qs[0], 'ex-q-on'), DOT = cls(qs[0], 'ex-q-dot');
  s.classList.add(ON);
  var dots = root.querySelector('[class$="ex-q-dots"]'), i = 0, d = root.ownerDocument;
  var ds = qs.map(function(q, k){ q.setAttribute('aria-roledescription', 'slide'); q.setAttribute('aria-label', (k + 1) + ' of ' + qs.length);
    var b = d.createElement('button'); b.type = 'button'; b.className = DOT; b.setAttribute('aria-label', 'Show testimonial ' + (k + 1));
    b.addEventListener('click', function(){ go(k); stop(); }); dots.appendChild(b); return b; });
  function go(n){ i = (n + qs.length) % qs.length;
    qs.forEach(function(q, k){ q.classList.toggle(CUR, k === i); q.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
    ds.forEach(function(b, k){ b.setAttribute('aria-current', k === i ? 'true' : 'false'); }); }
  root.querySelector('[class$="ex-q-prev"]').addEventListener('click', function(){ go(i - 1); stop(); });
  root.querySelector('[class$="ex-q-next"]').addEventListener('click', function(){ go(i + 1); stop(); });
  var x0 = null;
  tr.addEventListener('touchstart', function(e){ x0 = e.touches[0].clientX; }, {passive: true});
  tr.addEventListener('touchend', function(e){ if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) { go(i + (dx < 0 ? 1 : -1)); stop(); } x0 = null; });
  var t = null, rm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function start(){ if (!fields.autoplay || rm || t) return; tr.setAttribute('aria-live', 'off'); t = setInterval(function(){ go(i + 1); }, 8000); }
  function stop(){ if (t) { clearInterval(t); t = null; tr.setAttribute('aria-live', 'polite'); } }
  s.addEventListener('mouseenter', stop); s.addEventListener('mouseleave', start); s.addEventListener('focusin', stop);
  go(0); start();
}
```

## Team grid with square photos
Crop photos square with the face centered before upload (`scripts/square_crop.py`). The CSS keeps them square at every width.
```css
.ex-team-media{aspect-ratio:1/1;overflow:hidden;display:block;background:var(--pt-surface-sunken)}
.ex-team-img{width:100%;height:100%;object-fit:cover;object-position:center 22%;display:block}
.ex-team-link:focus-visible{outline:3px solid var(--pt-focus-ring);outline-offset:-3px}
.ex-team-arrow{width:44px;height:44px;border-radius:var(--pt-radius-pill)}
```
Use `object-position` only as a backup. The crop does the real work.

## CTA with a gradient button
Theme button tokens accept hex only. Put the gradient in the module CSS.
```css
.ex-cta-btn{display:inline-block;background:linear-gradient(135deg,#f59700 0%,#eb004f 100%);color:#ffffff;
  padding:14px 28px;border-radius:999px;text-decoration:none;font-weight:700;transition:filter .2s ease}
.ex-cta-btn:hover{filter:brightness(1.08)}
.ex-cta-btn:focus-visible{outline:3px solid #ffffff;outline-offset:3px}
```
White text on #f59700 is 2.26:1 and fails AA. Flag it. Offer a darker start color (for example #b35f00) if the user wants AA.

For an italic accent word in a heading, split the heading into fields (`heading`, `accent`, `heading_after`) and wrap the accent in `<em>`. Core heading blocks cannot do inline italics.

## Animated backgrounds
- Copy the source effect (canvas script or inline SVG animation) into the module script. Draw on a canvas the script creates.
- Pause when the section is off screen (IntersectionObserver) and under reduced motion.
- Compare with a short screen recording of both sites.

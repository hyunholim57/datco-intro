#!/usr/bin/env python3
"""index.tpl.html + assets/*.b64 → _site/index.html, og.png 생성."""
import glob
import os
import re

os.makedirs('_site', exist_ok=True)

html = open('index.tpl.html').read()
for path in glob.glob('assets/*.b64'):
    name = os.path.splitext(os.path.basename(path))[0]
    b64 = re.sub(r'\s+', '', open(path).read())
    placeholder = f'__B64_{name}__'
    assert placeholder in html, placeholder
    html = html.replace(placeholder, b64)

assert '__B64_' not in html, 'unresolved placeholder remains'
open('_site/index.html', 'w').write(html)
print('index.html built:', len(html))

# og.png: 히어로 영역 1200x630 스크린샷
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=2)
    pg.goto('file://' + os.path.abspath('_site/index.html'))
    pg.wait_for_timeout(2500)
    pg.evaluate("""() => {
      document.querySelectorAll('.lang-bar,.feature-list,.hero-close,.section-label,.modules,.doc-grid,.video-grid,.contact,footer')
        .forEach(e => e.style.display='none');
      document.body.style.background='#EFF1F3';
      const w=document.querySelector('.wrap'); w.style.maxWidth='900px'; w.style.padding='72px 40px';
      const h=document.querySelector('.hero'); h.style.padding='56px 56px 48px';
      const s=document.querySelector('.stat-band'); s.style.margin='30px 0 0';
    }""")
    pg.screenshot(path='_site/og.png', clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
    b.close()
print('og.png built')

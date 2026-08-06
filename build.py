#!/usr/bin/env python3
"""index.tpl.html + assets → _site/index.html, og.png 생성.

assets/parts/<name>.pNN (청크 분할본)이 있으면 그것을 이어붙여 사용하고,
없는 이름만 assets/<name>.b64 단일 파일을 사용한다.
"""
import glob
import os
import re
from collections import defaultdict

os.makedirs('_site', exist_ok=True)

# 1) 청크 분할 자산 조립
parts = defaultdict(list)
for path in sorted(glob.glob('assets/parts/*.p[0-9][0-9]')):
    base = os.path.basename(path)
    name, pno = base.rsplit('.p', 1)
    parts[name].append(path)

blobs = {}
for name, files in parts.items():
    blobs[name] = ''.join(re.sub(r'\s+', '', open(f).read()) for f in sorted(files))

# 2) 단일 .b64 파일 (청크가 없는 이름만)
for path in glob.glob('assets/*.b64'):
    name = os.path.splitext(os.path.basename(path))[0]
    if name not in blobs:
        blobs[name] = re.sub(r'\s+', '', open(path).read())

# 3) 템플릿 치환
html = open('index.tpl.html').read()
for name, b64 in blobs.items():
    placeholder = f'__B64_{name}__'
    assert placeholder in html, placeholder
    html = html.replace(placeholder, b64)

assert '__B64_' not in html, 'unresolved placeholder remains'
open('_site/index.html', 'w').write(html)
print('index.html built:', len(html))

# 4) og.png: 히어로 영역 1200x630 스크린샷
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

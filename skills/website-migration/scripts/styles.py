#!/usr/bin/env python3
"""Extract computed design tokens from a live page.
usage: styles.py URL [WIDTH] [out_dir]
Writes out_dir/styles.json (computed styles of key selectors), images.json
(src, natural size, alt, rendered width, y), backgrounds.txt (every CSS
background-image), fonts.json (loaded web fonts and @font-face urls) and
text.txt (visible body text, for real copy)."""
import asyncio, json, sys, os
from playwright.async_api import async_playwright
URL = sys.argv[1]; W = int(sys.argv[2]) if len(sys.argv) > 2 else 1440
OUT = sys.argv[3] if len(sys.argv) > 3 else 'src'
SEL = ['body', 'h1', 'h2', 'h3', 'h4', 'p', 'em,i', 'a[class*=button],a[class*=btn],button',
       'header,nav,[class*=nav]', 'footer', 'section', 'blockquote', 'input,select,textarea']
JS = """(sels)=>{const o=[];sels.forEach(sel=>document.querySelectorAll(sel).forEach((e,i)=>{if(i>3)return;
const c=getComputedStyle(e);o.push({sel,text:(e.innerText||'').slice(0,60),font:c.fontFamily,size:c.fontSize,
weight:c.fontWeight,style:c.fontStyle,lh:c.lineHeight,ls:c.letterSpacing,tt:c.textTransform,color:c.color,
bg:c.backgroundColor,bgi:c.backgroundImage.slice(0,300),radius:c.borderRadius,pad:c.padding,shadow:c.boxShadow,
transition:c.transition,animation:c.animationName})}));return o}"""
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": W, "height": 900})
        await pg.goto(URL, wait_until="load", timeout=60000); await pg.wait_for_timeout(2500)
        json.dump(await pg.evaluate(JS, SEL), open(f'{OUT}/styles.json', 'w'), indent=1)
        imgs = await pg.evaluate("()=>[...document.images].map(i=>({src:i.currentSrc||i.src,w:i.naturalWidth,h:i.naturalHeight,alt:i.alt,rw:Math.round(i.getBoundingClientRect().width),y:Math.round(i.getBoundingClientRect().top+scrollY)}))")
        json.dump(imgs, open(f'{OUT}/images.json', 'w'), indent=1)
        bgs = await pg.evaluate("()=>[...document.querySelectorAll('*')].map(e=>[e.className,getComputedStyle(e).backgroundImage]).filter(x=>x[1]!='none').map(x=>String(x[0]).slice(0,80)+' | '+x[1].slice(0,300))")
        open(f'{OUT}/backgrounds.txt', 'w').write('\n'.join(bgs))
        fonts = await pg.evaluate("""()=>{const r=[];for(const s of document.styleSheets){try{for(const x of s.cssRules){if(x.constructor.name=='CSSFontFaceRule')r.push(x.cssText.slice(0,400))}}catch(e){r.push('cross-origin sheet: '+s.href)}}
return {loaded:[...document.fonts].filter(f=>f.status=='loaded').map(f=>f.family+' '+f.weight+' '+f.style),faces:r}}""")
        json.dump(fonts, open(f'{OUT}/fonts.json', 'w'), indent=1)
        open(f'{OUT}/text.txt', 'w').write(await pg.evaluate("()=>document.body.innerText"))
        print('wrote', OUT); await b.close()
asyncio.run(main())

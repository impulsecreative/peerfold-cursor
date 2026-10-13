#!/usr/bin/env python3
"""Full-page live screenshots, cookie banner dismissed, lazy images triggered.
usage: shot.py BASE [WIDTH] /path1 /path2 ...   -> shots/<path__with__underscores>[_WIDTH].png
BASE e.g. https://<workspace>.peerfold.app/site or the source site ; WIDTH default 1440 (use 390 for mobile).
Set SHOT_PREFIX=src_ or SHOT_PREFIX=pf_ to keep source and build shots apart.
For pages with video, change wait_until to "load"."""
import asyncio, sys, os
from playwright.async_api import async_playwright
BASE = sys.argv[1].rstrip('/'); args = sys.argv[2:]
W = int(args[0]) if args and args[0].isdigit() else 1440
paths = [a for a in args if not a.isdigit()]; suffix = '' if W == 1440 else f'_{W}'
async def main():
    os.makedirs('shots', exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": W, "height": 900}, is_mobile=W < 600)
        for path in paths:
            pg = await ctx.new_page()
            r = await pg.goto(BASE + ('' if path == '/' else path), wait_until="networkidle", timeout=60000)
            for lab in ["Decline", "Reject", "Reject all", "Only necessary", "Accept"]:
                try: await pg.get_by_role("button", name=lab, exact=True).click(timeout=1200); break
                except Exception: pass
            await pg.wait_for_timeout(2500); print("url",pg.url)
            await pg.evaluate("""async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=500){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,100));}window.scrollTo(0,0);}""")
            await pg.wait_for_timeout(1200)
            name = os.environ.get("SHOT_PREFIX", "") + (path.strip('/').replace('/', '__') or 'home') + suffix
            await pg.screenshot(path=f"shots/{name}.png", full_page=True)
            print(path, r.status, f"shots/{name}.png"); await pg.close()
        await b.close()
asyncio.run(main())

#!/usr/bin/env python3
"""PUT one prepared image to the upload URL that mint_image_upload returned.
usage: upload.py FILE UPLOAD_URL CONTENT_TYPE FINAL_URL [map.json]
On HTTP 200 it records FILE -> FINAL_URL in map.json and appends a line
to log.md. No sites_confirm_image_upload call is needed for block images.
Upload URLs are short-lived and signed. Do not save them in files you share."""
import sys, json, os, subprocess
f, u, ct, final = sys.argv[1:5]; mp = sys.argv[5] if len(sys.argv) > 5 else 'map.json'
r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'PUT', '-H', f'Content-Type: {ct}',
                    '--data-binary', '@' + f, u], capture_output=True, text=True)
print(f, r.stdout)
m = json.load(open(mp)) if os.path.exists(mp) else {}
if r.stdout == '200': m[f] = final; json.dump(m, open(mp, 'w'), indent=1)
with open('log.md', 'a') as L: L.write(f"- upload {os.path.basename(f)} -> {r.stdout}\n")

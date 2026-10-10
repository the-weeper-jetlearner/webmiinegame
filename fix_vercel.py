"""Normalize pygbag output to `webmiinegame.*`.

Vercel clones into a folder literally named `path0`, so
`pygbag --build .` emits path0.apk/path0.tar.gz with index.html
hardcoded to `path0`. Locally the folder name varies too.
This renames whatever single .apk/.tar.gz was built to
webmiinegame.* and patches index.html to match.
"""
import glob
import os
import sys

WEB = os.path.join("build", "web")
NEW = "webmiinegame"

apks = sorted(glob.glob(os.path.join(WEB, "*.apk")))
tars = sorted(glob.glob(os.path.join(WEB, "*.tar.gz")))
print("found apks:", [os.path.basename(p) for p in apks])
print("found tars:", [os.path.basename(p) for p in tars])

old_names = set()
for p in apks + tars:
    stem = os.path.basename(p).removesuffix(".tar.gz").removesuffix(".apk")
    if stem != NEW:
        old_names.add(stem)

# Keep the newest apk/tar (the just-built game), drop stale ones.
def newest(paths):
    return max(paths, key=os.path.getmtime) if paths else None

keep_apk, keep_tar = newest(apks), newest(tars)
for p in apks + tars:
    if p not in (keep_apk, keep_tar):
        os.remove(p)
        print("removed stale:", os.path.basename(p))

if keep_apk:
    dst = os.path.join(WEB, NEW + ".apk")
    if os.path.abspath(keep_apk) != os.path.abspath(dst):
        os.replace(keep_apk, dst)
        print(f"renamed {os.path.basename(keep_apk)} -> {NEW}.apk")
if keep_tar:
    dst = os.path.join(WEB, NEW + ".tar.gz")
    if os.path.abspath(keep_tar) != os.path.abspath(dst):
        os.replace(keep_tar, dst)
        print(f"renamed {os.path.basename(keep_tar)} -> {NEW}.tar.gz")

index = os.path.join(WEB, "index.html")
if not os.path.exists(index):
    print("index.html missing", file=sys.stderr)
    sys.exit(1)
with open(index, encoding="utf-8") as f:
    html = f.read()
for old in sorted(old_names):
    if old:
        html = html.replace(old, NEW)
with open(index, "w", encoding="utf-8") as f:
    f.write(html)
print("patched index.html old names:", sorted(old_names) or "none")

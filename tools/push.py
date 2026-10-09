"""Push files from this folder to github.com/nicholasbeskow/study-board via the Contents API.
No git needed (git can't clean its lock files in the connected folder).
Token: ~/Documents/Manhattan Project/.study-board-token (one line, never printed).
Usage (from the study-board folder): python3 -I tools/push.py board.json [index.html ...]
Prints one line per file: pushed / unchanged / FAILED <code>."""
import base64, json, os, sys, urllib.request, urllib.error

REPO = "nicholasbeskow/study-board"
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tok = open(os.path.join(os.path.dirname(here), ".study-board-token"), encoding="utf-8").read().strip()

def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
        headers={"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json", "User-Agent": "study-board-push"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e: return e.code, {}

bad = 0
for rel in sys.argv[1:]:
    raw = open(os.path.join(here, rel), "rb").read()
    url = f"https://api.github.com/repos/{REPO}/contents/{rel}"
    code, cur = call("GET", url)
    sha = cur.get("sha") if code == 200 else None
    if sha and base64.b64decode(cur.get("content", "")) == raw:
        print("unchanged", rel); continue
    body = {"message": f"update {rel}", "content": base64.b64encode(raw).decode(), "branch": "main"}
    if sha: body["sha"] = sha
    code, _ = call("PUT", url, body)
    if code in (200, 201): print("pushed", rel)
    else: print("FAILED", code, rel); bad += 1
sys.exit(1 if bad else 0)

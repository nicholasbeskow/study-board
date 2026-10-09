"""Hourly: merge an ArtifactData out_dir dump into board.json (public-safe fields only).
Usage: python3 -I build_board_json.py <dump_dir> <out_json>"""
import json, os, sys, glob
dump, out = sys.argv[1], sys.argv[2]
def unwrap(d):
    return d["data"] if isinstance(d, dict) and isinstance(d.get("data"), dict) else d
def docs(coll):
    res = []
    for p in sorted(glob.glob(os.path.join(dump, coll, "*.json"))):
        d = dict(unwrap(json.load(open(p, encoding="utf-8"))))
        d["id"] = os.path.splitext(os.path.basename(p))[0]
        res.append(d)
    return res
meta = {}
mp = os.path.join(dump, "meta", "state.json")
if os.path.exists(mp):
    m = unwrap(json.load(open(mp, encoding="utf-8")))
    meta = {k: m.get(k) for k in ("course", "currentTest", "refreshedAt", "refreshedBy")}
LEC_KEYS = ("id","test","code","codeGuess","title","instructor","date","start","end","mandatory","where","kind","order","box","counts","videos","stages","topic")
TEST_KEYS = ("id","label","course","range","examDate","order","lastOfCourse","box","deliverables","resources")
board = {
    "meta": meta,
    "tests": [{k: t[k] for k in TEST_KEYS if k in t} for t in docs("tests")],
    "lectures": [{k: l[k] for k in LEC_KEYS if k in l} for l in docs("lectures")],
    "compare": {c["id"]: {k: v for k, v in c.items() if k != "id"} for c in docs("compare")},
}
new = json.dumps(board, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
old = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
if new == old: print("unchanged"); sys.exit(0)
open(out, "w", encoding="utf-8").write(new); print("changed", len(new))

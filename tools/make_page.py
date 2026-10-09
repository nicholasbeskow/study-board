"""One-time: turn the claude.ai board page into a read-only public page that reads board.json."""
import re, sys
src, out = sys.argv[1], sys.argv[2]
h = open(src, encoding="utf-8").read()
h = h.replace("</body></html>\n</body></html>", "</body></html>").rstrip()
if h.endswith("</body></html></body></html>"): h = h[: -len("</body></html>")]
h = h.replace("<meta charset=utf8>", '<meta charset=utf8><meta name="robots" content="noindex,nofollow">', 1)
# hide owner-only sidebar panels (jobs + notes)
for t in ("Claude jobs", "Notes from the last refresh"):
    a = f'<section class="day">\n      <h2>{t}</h2>'
    assert a in h, t
    h = h.replace(a, a.replace('<section class="day">', '<section class="day" hidden>'))
start = h.index("  // ---- capabilities ----")
end = h.index("})();\n</script>", start)
loader = r'''  // ---- public copy: read board.json (written hourly from the board's database) ----
  async function load() {
    try {
      const r = await fetch("board.json?t=" + Date.now(), { cache: "no-store" });
      if (!r.ok) throw new Error(r.status);
      const b = await r.json();
      db = {}; state.owner = false;
      state.meta = b.meta || null;
      state.tests = b.tests || [];
      state.lectures = (b.lectures || []).map((l) => {
        const st = { ...(l.stages || {}) };
        if (st.pool && st.pool.s !== "done") st.pool = { s: st.pool.s };
        return { ...l, stages: st };
      });
      state.compare = b.compare || {};
      state.jobs = [];
      renderAll(); state.firstPaint = false;
    } catch (e) { $("freshText").textContent = "Couldn't load the board"; }
  }
  load();
  setInterval(load, 5 * 60000);
'''
h = h[:start] + loader + h[end:]
open(out, "w", encoding="utf-8").write(h)
print("ok", len(h))

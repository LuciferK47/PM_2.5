"""Write SPEAKER_NOTES.md from the \\note{...} blocks of slides/beamer/main.tex.

Run after make_figures.py (number macros come from slides/beamer/tables/numbers.tex):
    python tools/extract_notes.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "slides/beamer/main.tex").read_text()
SRC = SRC[SRC.index("\\begin{document}"):]
macros = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{(.*)\}$", (ROOT / "slides/beamer/tables/numbers.tex").read_text(), re.M))


def balanced(s, i):
    """s[i] == '{': return (content, index after the closing brace)."""
    depth, j = 0, i
    while j < len(s):
        depth += s[j] == "{"
        depth -= s[j] == "}"
        j += 1
        if depth == 0:
            return s[i + 1:j - 1], j
    raise ValueError("unbalanced braces")


def clean(t):
    for k in sorted(macros, key=len, reverse=True):
        t = re.sub(rf"\\{k}(?![A-Za-z])\s?", lambda m, k=k: macros[k] + " ", t)
    t = t.replace("\\ugm{}", "µg/m³").replace("\\ugm", "µg/m³")
    t = re.sub(r"PM\$_\{2\.5\}\$", "PM2.5", t)
    t = re.sub(r"\$([^$]*)\$", lambda m: m.group(1).replace("\\", ""), t)
    t = t.replace("\\%", "%").replace("{,}", ",").replace("$", "")
    return re.sub(r"\s+", " ", t).strip()


out = ["# Speaker notes: Forecasting Delhi's PM2.5 (MATH F428)", "",
       "What to say on each slide. Numbers are filled in from the same macros as the slides. Slide numbers count every frame in `main.tex`.", ""]
n = 0
sec = ""
secinfo = ""
for m in re.finditer(r"\\renewcommand\{\\secinfo\}\{|\\section\{([^}]*)\}|\\begin\{frame\}(?:\[[^\]]*\])?(\{)", SRC):
    if m.group(0).startswith("\\renewcommand"):
        secinfo, _ = balanced(SRC, m.end() - 1)
        continue
    if m.group(1) is not None and not m.group(0).startswith("\\begin"):
        sec = m.group(1)
        out += [f"## {sec}", ""]
        continue
    raw_title, after = balanced(SRC, m.end() - 1)
    title = clean(raw_title.replace("\\ ", "Title slide")) or "Title slide"
    end = SRC.index("\\end{frame}", after)
    body = SRC[after:end]
    k = body.find("\\note{")
    note = clean(balanced(body, k + 5)[0]) if k >= 0 else "(no note)"
    n += 1
    out += [f"**Slide {n}: {title}.** {note}", ""]
(ROOT / "SPEAKER_NOTES.md").write_text("\n".join(out))
print("slides:", n)

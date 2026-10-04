"""Generate the profile's SVG assets (light + dark variants) into ../assets.

Edit the text/numbers below and re-run:  python scripts/build_assets.py
Only facts that also appear in README.md belong here.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": dict(text="#1f2328", muted="#59636e", border="#d1d9e0", card="#ffffff", accent="#0b7a6e", gold="#b7791f", on_gold="#ffffff"),
    "dark": dict(text="#e6edf3", muted="#9198a1", border="#3d444d", card="#151b23", accent="#2dd4bf", gold="#e3b341", on_gold="#1f2328"),
}


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title>{body}</svg>\n')


def text(x, y, s, size, fill, weight=400, family=SANS, anchor="start", spacing=0, extra=""):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}{extra}>{escape(s)}</text>')


# ---------------------------------------------------------------- banner
STAGES = [("data", "speech · text"), ("fine-tune", "QLoRA · SFT"), ("evaluate", "WER · BERTScore"),
          ("serve", "vLLM · Kubernetes"), ("ship", "FastAPI · React")]


def banner(t):
    w, h, y = 900, 130, 52
    xs = [90 + i * 180 for i in range(len(STAGES))]
    dur, travel = 6, 0.75  # packet crosses in the first 75% of each cycle
    b = [f'<line x1="{xs[0]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{t["border"]}" stroke-width="2"/>']
    for i, (name, sub) in enumerate(STAGES):
        x = xs[i]
        at = travel * i / (len(STAGES) - 1)
        # the node lights up when the packet reaches it
        if at == 0:
            kt, vals = "0;0.12;1", "1;0.3;0.3"
        else:
            kt = f"0;{at - 0.01:.3f};{at:.3f};{min(at + 0.12, 0.99):.3f};1"
            vals = "0.3;0.3;1;0.3;0.3"
        b.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{t["card"]}" stroke="{t["accent"]}" stroke-width="2"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{t["accent"]}" opacity="0.3">'
                 f'<animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" '
                 f'keyTimes="{kt}" values="{vals}"/></circle>')
        b.append(text(x, y + 42, name, 19, t["text"], 600, anchor="middle"))
        b.append(text(x, y + 66, sub, 14, t["muted"], family=MONO, anchor="middle"))
    b.append(f'<circle r="5" fill="{t["accent"]}">'
             f'<animateMotion dur="{dur}s" repeatCount="indefinite" calcMode="linear" '
             f'keyPoints="0;1;1" keyTimes="0;{travel};1" path="M{xs[0]},{y} L{xs[-1]},{y}"/>'
             f'<animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" '
             f'keyTimes="0;0.05;{travel};{travel + 0.1};1" values="0;1;1;0;0"/></circle>')
    return svg(w, h, "".join(b), "From data to fine-tuning, evaluation, serving and shipping")


# ---------------------------------------------------------------- typing line
LINES = [
    "Adapting LLMs & speech models to Tunisian Arabic",
    "Contributing to kubernetes-sigs/lws",
    "Turning models into APIs, infra & products",
]


def typing(t):
    size, cw, x0, y = 20, 12, 36, 29  # cw: forced advance per char via textLength
    w = x0 + max(map(len, LINES)) * cw + 30
    type_s, hold, erase_s, gap = 0.055, 2.2, 0.02, 0.4
    # build a timeline of (time, line, chars visible)
    events, now = [], 0.0
    for i, line in enumerate(LINES):
        for n in range(len(line) + 1):
            events.append((now, i, n)); now += type_s
        now += hold
        for n in range(len(line), -1, -1):
            events.append((now, i, n)); now += erase_s
        now += gap
    total = now

    def anim(attr, pick):
        kts, vals = [], []
        for tm, i, n in events:
            v = pick(i, n)
            if vals and vals[-1] == v:
                continue
            kts.append(f"{tm / total:.4f}"); vals.append(v)
        kts[0] = "0"
        return (f'<animate attributeName="{attr}" dur="{total:.2f}s" repeatCount="indefinite" '
                f'calcMode="discrete" keyTimes="{";".join(kts)}" values="{";".join(vals)}"/>')

    b = [text(12, y, "›", size, t["accent"], 700, MONO)]
    for i, line in enumerate(LINES):
        b.append(f'<clipPath id="c{i}"><rect x="{x0}" y="0" height="40" width="0">'
                 + anim("width", lambda j, n, i=i: str(n * cw) if j == i else "0") + '</rect></clipPath>')
        b.append(f'<g clip-path="url(#c{i})">'
                 + text(x0, y, line, size, t["text"], 500, MONO,
                        extra=f' textLength="{len(line) * cw}" lengthAdjust="spacing"') + '</g>')
    b.append(f'<rect y="{y - 17}" width="2" height="21" fill="{t["accent"]}" x="{x0}">'
             + anim("x", lambda j, n: str(x0 + n * cw + 2))
             + '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect>')
    return svg(w, 40, "".join(b), " / ".join(LINES))


# ---------------------------------------------------------------- cards
def pills(x, y, labels, t, size=15):
    out = []
    for s in labels:
        pw = len(s) * size * 0.58 + 22
        out.append(f'<rect x="{x}" y="{y - size - 6}" width="{pw:.0f}" height="{size + 13}" rx="{(size + 13) / 2}" '
                   f'fill="none" stroke="{t["border"]}"/>')
        out.append(text(x + pw / 2, y, s, size, t["muted"], family=MONO, anchor="middle"))
        x += pw + 10
    return "".join(out)


def frame(w, h, t):
    return f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>'


def wide_card(t, badge, kicker, title, lines, tags, alt):
    w, h = 900, 230
    b = [frame(w, h, t), badge,
         text(200, 58, kicker, 16, t["muted"], 600, spacing=1.5),
         text(200, 100, title, 40, t["text"], 700)]
    for i, s in enumerate(lines):
        b.append(text(200, 140 + i * 28, s, 21, t["text"]))
    b.append(pills(200, 206, tags, t))
    return svg(w, h, "".join(b), alt)


def card_indabax(t):
    medal = (f'<circle cx="112" cy="115" r="56" fill="{t["gold"]}"/>'
             f'<circle cx="112" cy="115" r="56" fill="none" stroke="{t["gold"]}" stroke-width="2">'
             '<animate attributeName="r" values="56;70" dur="2.8s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0.7;0" dur="2.8s" repeatCount="indefinite"/></circle>'
             + text(112, 128, "1st", 36, t["on_gold"], 800, anchor="middle"))
    return wide_card(t, medal, "INDABAX TUNISIA 2025 · AI HACKATHON", "1st Place",
                     ["Predicts eNodeB anomalies in telecom networks and suggests",
                      "resolutions with a fine-tuned BART Large model."],
                     ["XGBoost", "LightGBM", "BART Large"],
                     "1st Place, IndabaX Tunisia 2025 AI Hackathon")


def card_tounsilm(t):
    metric = (text(112, 122, "76.2%", 40, t["accent"], 800, anchor="middle")
              + text(112, 150, "token accuracy", 15, t["muted"], anchor="middle"))
    return wide_card(t, metric, "LLM FOR TUNISIAN ARABIC · HUGGING FACE", "TounsiLM-8B",
                     ["QLoRA continued pretraining on 85M tokens + SFT on 31.7K",
                      "pairs, built on Aya-Expanse-8B after benchmarking 5 LLMs."],
                     ["QLoRA", "SFT", "Aya-Expanse-8B"],
                     "TounsiLM-8B: 76.2% token accuracy")


ASSETS = {"banner": banner, "typing": typing, "card-indabax": card_indabax, "card-tounsilm": card_tounsilm}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in ASSETS.items():
        for theme, tokens in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(fn(tokens), encoding="utf-8")
            print(f"assets/{name}-{theme}.svg")

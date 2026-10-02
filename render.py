"""THEZIP card renderer. Usage: python3 render.py cards.json OUT_DIR
cards.json = {"day":"MON|WED|FRI","cards":[...]} (see example_cards.json)"""
import json, sys, pathlib, subprocess, urllib.request, zipfile, io, html

ROOT = pathlib.Path(__file__).resolve().parent
FONT_DIR = ROOT / "fonts"
DAY = {
    "MON": {"label": "K-BEAUTY IN USA", "accent": "#ED93B1", "ink": "#993556"},
    "WED": {"label": "US MARKETING",    "accent": "#85B7EB", "ink": "#185FA5"},
    "FRI": {"label": "POP-UP IN USA",   "accent": "#FAC775", "ink": "#854F0B"},
}
DARK, PAPER = "#141414", "#ECEAE4"

def ensure_font():
    if (FONT_DIR / "Pretendard-Bold.otf").exists():
        return
    url = "https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip"
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(url).read()))
    FONT_DIR.mkdir(exist_ok=True)
    for n in z.namelist():
        if n.startswith("public/static/Pretendard-") and n.endswith(".otf"):
            (FONT_DIR / pathlib.Path(n).name).write_bytes(z.read(n))

def rich(t):
    # **bold** -> <b>, newline -> <br>
    t = html.escape(t)
    parts = t.split("**")
    t = "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))
    return t.replace("\n", "<br>")

def css():
    w = [("Regular", 400), ("Medium", 500), ("Bold", 700), ("ExtraBold", 800)]
    f = "".join(f"@font-face{{font-family:P;src:url('file://{FONT_DIR}/Pretendard-{n}.otf');font-weight:{v}}}" for n, v in w)
    return f"""<style>{f}*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:P,'Noto Sans CJK KR',sans-serif;letter-spacing:-0.02em;overflow:hidden;word-break:keep-all;position:relative}}
.top{{position:absolute;top:64px;left:80px;right:80px;display:flex;justify-content:space-between;font-weight:800;font-size:30px;letter-spacing:0.18em}}
.rule{{position:absolute;top:124px;left:80px;right:80px;height:2px}}
.src{{position:absolute;bottom:56px;left:80px;right:80px;font-size:22px;color:#888780}}
.wrap{{position:absolute;top:200px;left:80px;right:80px}}
.kick{{font-size:26px;font-weight:700;letter-spacing:0.12em;margin-bottom:28px}}
.h{{font-size:66px;font-weight:800;line-height:1.25;color:#111;margin-bottom:48px}}
.t{{font-size:36px;line-height:1.7;color:#444441}} .t b{{color:#111;font-weight:700}}
.photo{{width:100%;height:420px;object-fit:cover;border-radius:8px;margin-bottom:44px;display:block}}</style>"""

def frame(bg, fg, num_color, num, inner, src=""):
    rule = "#3a3a3a" if bg == DARK else "#111"
    s = f'<div class=src>{html.escape(src)}</div>' if src else ""
    return f"""<html><head>{css()}</head><body style="background:{bg};color:{fg}">
<div class=top><span>THEZIP</span><span style="color:{num_color}">{num}</span></div>
<div class=rule style="background:{rule}"></div>{inner}{s}</body></html>"""

def build(card, i, d):
    k = card["type"]
    num = f"{i:02d}"
    if k == "cover":
        bgimg = ""
        if card.get("image"):
            bgimg = f'<img src="{card["image"]}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0.45">'
        inner = f"""{bgimg}<div style="position:absolute;left:80px;right:80px;bottom:150px">
<div style="font-size:28px;font-weight:700;letter-spacing:0.12em;color:{d['accent']};margin-bottom:36px">{d['label']}</div>
<div style="font-size:104px;font-weight:800;line-height:1.2">{rich(card['title'])}</div>
<div style="font-size:32px;color:#B4B2A9;margin-top:40px">{rich(card.get('sub',''))}</div></div>"""
        return frame(DARK, "#fff", d["accent"], card.get("day_tag", ""), inner, card.get("source", ""))
    if k == "outro":
        return f"""<html><head>{css()}</head><body style="background:{DARK};color:#fff">
<div style="position:absolute;top:50%;left:0;right:0;transform:translateY(-50%);text-align:center">
<div style="font-size:96px;font-weight:800;letter-spacing:0.16em;margin-bottom:44px">THEZIP</div>
<div style="font-size:36px;color:#B4B2A9;line-height:1.7">미국 시장을 한 장에 압축<br>월 K-뷰티 · 수 마케팅 · 금 팝업</div></div>
<div style="position:absolute;bottom:72px;left:0;right:0;text-align:center;font-size:28px;color:#888780">@thezipus</div></body></html>"""
    head = f'<div class=kick style="color:{d["ink"]}">{html.escape(card.get("kicker",""))}</div><div class=h>{rich(card["title"])}</div>'
    extra = ""
    if k == "stat":
        extra = f"""<div style="display:flex;align-items:flex-end;gap:36px;margin-bottom:56px">
<div style="font-size:200px;font-weight:800;line-height:0.9;color:#111">{html.escape(card['stat'])}</div>
<div style="font-size:30px;line-height:1.6;color:#5F5E5A;padding-bottom:14px">{rich(card.get('stat_note',''))}</div></div>"""
    if k == "points":
        pts = "".join(f'<div style="display:flex;gap:28px;padding:30px 0;border-top:2px solid #111"><div style="font-size:34px;font-weight:800;color:{d["ink"]}">{j:02d}</div><div class=t style="color:#111">{rich(p)}</div></div>' for j, p in enumerate(card["points"], 1))
        return frame(PAPER, "#111", "#5F5E5A", num, f'<div class=wrap>{head}{pts}</div>', card.get("source", ""))
    if card.get("image"):
        extra += f'<img class=photo src="{card["image"]}">'
    body = f'<div class=t>{rich(card.get("text",""))}</div>'
    return frame(PAPER, "#111", "#5F5E5A", num, f'<div class=wrap>{head}{extra}{body}</div>', card.get("source", ""))

def main(spec, out):
    ensure_font()
    data = json.loads(pathlib.Path(spec).read_text(encoding="utf-8"))
    d = DAY[data["day"]]
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, c in enumerate(data["cards"], 1):
            c.setdefault("day_tag", data["day"])
            h = out / f"_{i:02d}.html"; h.write_text(build(c, i, d), encoding="utf-8")
            pg.goto("file://" + str(h.resolve())); pg.wait_for_timeout(300)
            pg.screenshot(path=str(out / f"{i:02d}.png")); h.unlink()
        b.close()
    print("rendered", len(data["cards"]), "cards ->", out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

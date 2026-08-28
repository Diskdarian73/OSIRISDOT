"""Renderers: a terminal sweep for the console, a self-contained CRT brief for the browser.

The HTML matches the archive pages already in this repo — phosphor on
duat-black, Courier New, uppercase, scanlines over grain over vignette,
corner brackets. Colors are canon-lock v4.1 tokens only; no new hex enters
the palette here.

Canon rule enforced in the markup: green and crimson meet at hard edges only.
Every item carries exactly one pole class and there is no gradient anywhere
between --phosphor and --crimson in this stylesheet.
"""

import datetime
import html
from typing import Any, Dict, List

# canon-lock v4.1 — do not introduce hex values outside this block.
TOKENS = {
    "duat-black": "#010103",
    "lake-midnight": "#0B1226",
    "phosphor": "#00FF46",
    "phosphor-dim": "#0A8A2E",
    "crimson": "#FF3A1A",
    "crimson-dim": "#7A1A0C",
    "agi-gold": "#FFC93C",
    "bone": "#D8D2C4",
}

POLE_GLYPH = {"SIGNAL": "◉", "NETWORK": "△", "UNVERIFIED": "○"}


def _stamp(epoch: float) -> str:
    if not epoch:
        return "--"
    return datetime.datetime.fromtimestamp(
        epoch, datetime.timezone.utc).strftime("%Y-%m-%d")


def _bar(value: float, width: int = 12) -> str:
    filled = max(0, min(width, int(round(value * width))))
    return "█" * filled + "·" * (width - filled)


def terminal(report: Dict[str, Any]) -> str:
    """Plain-text sweep for stdout. Reads like the archive terminals."""
    L: List[str] = []
    meta = report["meta"]
    L.append("")
    L.append("  OSIRIS.EXE // RECON SWEEP")
    L.append("  " + "─" * 62)
    L.append(f"  WINDOW      {meta['from']} .. {meta['to']}  ({meta['window_days']}d)")
    L.append(f"  LANES       {', '.join(meta['lanes'])}")
    L.append(f"  CAPTURED    {meta['total']} items / {meta['sources_live']} of "
             f"{meta['sources_tried']} sources live")
    L.append(f"  SIGNAL      {meta['signal']}    NETWORK  {meta['network']}"
             f"    UNVERIFIED  {meta['unverified']}")
    L.append("")

    if not report["clusters"]:
        L.append("  NO CARRIER. Sweep returned nothing above the floor.")
        L.append("  This is a valid result, not a fault — the scene was quiet.")
        L.append("")
        return "\n".join(L)

    for n, c in enumerate(report["clusters"], 1):
        items = c["items"]

        def line(item: Dict[str, Any], indent: str) -> None:
            eng = (f"{item['score']}pts {item['comments']}c"
                   if item["scored"] else "unmeasured")
            L.append(f"{indent}{item['venue']} · {eng} · "
                     f"{_stamp(item.get('created'))} · {item['author']}")
            L.append(f"{indent}{item['url']}")

        if len(items) == 1:
            # One item is not a cluster — print it as itself rather than
            # repeating the same title as heading and then as sole member.
            item = items[0]
            glyph = POLE_GLYPH.get(item["pole"], "○")
            L.append(f"  [{n:02d}] {glyph} {item['title'][:62]}")
            line(item, "       ")
        else:
            L.append(f"  [{n:02d}] {c['title'][:64]}")
            L.append(f"       {len(items)} items · {'/'.join(c['sources'])} "
                     f"· signal {c['signal']} / network {c['network']}")
            for item in items[:4]:
                glyph = POLE_GLYPH.get(item["pole"], "○")
                L.append(f"       {glyph} {item['title'][:58]}")
                line(item, "         ")
        L.append("")

    L.append("  " + "─" * 62)
    L.append("  ◉ SIGNAL = argued about   △ NETWORK = upvoted and scrolled past")
    L.append("  ○ UNVERIFIED = no engagement data on this surface")
    L.append("  ARCHIVE: CHI/HMB/047 // DO NOT ANSWER")
    L.append("")
    return "\n".join(L)


def _item_html(item: Dict[str, Any]) -> str:
    pole = item["pole"].lower()
    eng = (f"{item['score']} pts · {item['comments']} comments"
           if item["scored"] else "unmeasured surface")
    return f"""      <li class="item {pole}">
        <a class="t" href="{html.escape(item['url'])}" target="_blank" rel="noopener noreferrer">{html.escape(item['title'])}</a>
        <div class="m"><span class="pole">{item['pole']}</span> {html.escape(item['venue'])} · {eng} · {_stamp(item.get('created'))} · {html.escape(item['author'])}</div>
      </li>"""


def _cluster_html(n: int, c: Dict[str, Any]) -> str:
    """One cluster block.

    A single-item cluster is rendered as the item itself — heading as the
    link, metadata beneath. Printing the heading and then the same title
    again as its only list entry says the same thing twice.
    """
    meta = (f"{len(c['items'])} item(s) · {'/'.join(c['sources'])} · "
            f"signal {c['signal']} / network {c['network']}")
    items = c["items"]
    if len(items) == 1:
        item = items[0]
        eng = (f"{item['score']} pts · {item['comments']} comments"
               if item["scored"] else "unmeasured surface")
        return f"""    <section class="cluster solo {item['pole'].lower()}">
      <h2><i>{n:02d}</i> <a class="t" href="{html.escape(item['url'])}" target="_blank" rel="noopener noreferrer">{html.escape(item['title'])}</a></h2>
      <div class="cmeta"><span class="pole">{item['pole']}</span> {html.escape(item['venue'])} · {eng} · {_stamp(item.get('created'))} · {html.escape(item['author'])}</div>
    </section>"""
    return f"""    <section class="cluster">
      <h2><i>{n:02d}</i> {html.escape(c['title'])}</h2>
      <div class="cmeta">{meta}</div>
      <ul>
{chr(10).join(_item_html(i) for i in items[:6])}
      </ul>
    </section>"""


def html_brief(report: Dict[str, Any]) -> str:
    meta = report["meta"]
    clusters = report["clusters"]

    if clusters:
        body = "\n".join(_cluster_html(n, c) for n, c in enumerate(clusters, 1))
    else:
        body = ('    <section class="cluster"><h2>NO CARRIER</h2>'
                '<div class="cmeta">Sweep returned nothing above the floor. '
                'This is a valid result, not a fault.</div></section>')

    t = TOKENS
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="{t['duat-black']}">
<title>OSIRIS.EXE // RECON SWEEP {meta['to']}</title>
<meta name="description" content="Recon sweep of the OSIRIS.EXE adjacent scene, {meta['from']} to {meta['to']}">
<style>
:root{{
  --duat:{t['duat-black']}; --midnight:{t['lake-midnight']};
  --phosphor:{t['phosphor']}; --phosphor-dim:{t['phosphor-dim']};
  --crimson:{t['crimson']}; --crimson-dim:{t['crimson-dim']};
  --gold:{t['agi-gold']}; --bone:{t['bone']};
  /* Body text is --bone, a canon token. The archive pages already in this
     repo use #dfffe7, which is NOT in canon-lock v4.1's palette; canon is
     rule zero, so this brief uses the token. Flip --text to bring it back. */
  --line:rgba(0,255,70,.22); --text:var(--bone);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--duat);color:var(--text);
  font:12px/1.65 "Courier New",ui-monospace,monospace;text-transform:uppercase;
  padding:clamp(16px,4vw,48px)}}
.scan,.grain,.vig{{position:fixed;inset:0;pointer-events:none;z-index:9}}
.scan{{background:repeating-linear-gradient(0deg,rgba(0,0,0,.17) 0 1px,rgba(0,255,70,.025) 1px 2px);mix-blend-mode:screen}}
.grain{{opacity:.10;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.95' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");animation:grain .16s steps(2) infinite}}
.vig{{background:radial-gradient(circle,transparent 34%,rgba(0,5,2,.28) 66%,#000 120%)}}
.corner{{position:fixed;width:20px;height:20px;z-index:10;border-color:var(--phosphor);opacity:.55}}
.tl{{left:10px;top:10px;border-left:1px solid;border-top:1px solid}}
.tr{{right:10px;top:10px;border-right:1px solid;border-top:1px solid}}
.bl{{left:10px;bottom:10px;border-left:1px solid;border-bottom:1px solid}}
.br{{right:10px;bottom:10px;border-right:1px solid;border-bottom:1px solid}}
main{{position:relative;z-index:2;max-width:940px;margin:0 auto}}
.eyebrow{{color:var(--phosphor);font-size:9px;letter-spacing:.2em}}
.led{{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:8px;
  background:var(--phosphor);box-shadow:0 0 10px var(--phosphor);animation:blink 1.5s steps(1) infinite}}
h1{{margin:10px 0 0;font:900 clamp(30px,5.4vw,62px)/.86 "Arial Black",Impact,sans-serif;letter-spacing:-.06em}}
h1 span{{color:var(--phosphor)}}
.telemetry{{margin:26px 0 34px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:6px 0}}
.row{{display:flex;justify-content:space-between;gap:16px;padding:5px 0;border-bottom:1px dotted rgba(0,255,70,.13);color:rgba(216,210,196,.66)}}
.row:last-child{{border-bottom:0}}
.row b{{color:var(--text);font-weight:400;text-align:right}}
.cluster{{margin:0 0 34px;border-left:1px solid var(--line);padding-left:clamp(12px,2vw,22px)}}
h2{{margin:0;font-size:14px;font-weight:700;color:var(--text);letter-spacing:.02em;line-height:1.4}}
h2 i{{color:var(--phosphor);font-style:normal;margin-right:10px}}
.cmeta{{color:rgba(216,210,196,.62);font-size:9px;letter-spacing:.12em;margin:6px 0 14px}}
ul{{list-style:none;margin:0;padding:0}}
.item{{padding:9px 0 9px 14px;border-bottom:1px dotted rgba(0,255,70,.10);border-left:2px solid transparent}}
.item:last-child{{border-bottom:0}}
.item .t{{color:var(--text);text-decoration:none;border-bottom:1px solid transparent}}
.item .t:hover,.item .t:focus-visible{{border-bottom-color:currentColor;outline:none}}
.m{{color:rgba(216,210,196,.60);font-size:9px;letter-spacing:.1em;margin-top:5px}}
.pole{{font-weight:700;letter-spacing:.14em;margin-right:6px}}
/* The poles never blend: one flat token per state, no gradient between them. */
.item.signal{{border-left-color:var(--phosphor)}}
.item.signal .pole{{color:var(--phosphor)}}
.item.signal .t:hover{{color:var(--phosphor)}}
.item.network{{border-left-color:var(--crimson)}}
.item.network .pole{{color:var(--crimson)}}
.item.network .t:hover{{color:var(--crimson)}}
.item.unverified{{border-left-color:var(--crimson-dim)}}
.item.unverified .pole{{color:var(--bone)}}
.item.unverified .t{{color:var(--bone)}}
.cluster.solo{{border-left-width:2px}}
.cluster.solo.signal{{border-left-color:var(--phosphor)}}
.cluster.solo.signal .pole{{color:var(--phosphor)}}
.cluster.solo.network{{border-left-color:var(--crimson)}}
.cluster.solo.network .pole{{color:var(--crimson)}}
.cluster.solo.unverified{{border-left-color:var(--crimson-dim)}}
.cluster.solo.unverified .pole{{color:var(--bone)}}
h2 .t{{color:inherit;text-decoration:none;border-bottom:1px solid transparent}}
h2 .t:hover,h2 .t:focus-visible{{border-bottom-color:var(--phosphor);outline:none}}
.legend{{margin-top:40px;border-top:1px solid var(--line);padding-top:16px;
  color:rgba(216,210,196,.62);font-size:9px;letter-spacing:.12em;line-height:2}}
.legend b{{font-weight:700}}
.legend .s{{color:var(--phosphor)}} .legend .n{{color:var(--crimson)}} .legend .u{{color:var(--bone)}}
.sig{{margin-top:22px;color:var(--phosphor-dim);font-size:9px;letter-spacing:.2em}}
@keyframes grain{{0%{{transform:translate(0)}}25%{{transform:translate(-2%,1%)}}50%{{transform:translate(1%,-2%)}}75%{{transform:translate(2%,2%)}}}}
@keyframes blink{{0%,70%{{opacity:1}}71%,78%{{opacity:.15}}79%{{opacity:1}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
@media(max-width:640px){{.row{{font-size:10px}}h2{{font-size:12px}}}}
</style>
</head>
<body>
<div class="scan"></div><div class="grain"></div><div class="vig"></div>
<i class="corner tl"></i><i class="corner tr"></i><i class="corner bl"></i><i class="corner br"></i>
<main>
  <header>
    <div class="eyebrow"><i class="led"></i>recon sweep // adjacent scene</div>
    <h1>OSIRIS<span>.EXE</span></h1>
  </header>
  <div class="telemetry">
    <div class="row"><span>window</span><b>{meta['from']} .. {meta['to']} ({meta['window_days']}d)</b></div>
    <div class="row"><span>lanes</span><b>{html.escape(', '.join(meta['lanes']))}</b></div>
    <div class="row"><span>captured</span><b>{meta['total']} items</b></div>
    <div class="row"><span>sources live</span><b>{meta['sources_live']} / {meta['sources_tried']}</b></div>
    <div class="row"><span>signal / network / unverified</span><b>{meta['signal']} / {meta['network']} / {meta['unverified']}</b></div>
  </div>
{body}
  <div class="legend">
    <div><b class="s">SIGNAL</b> — argued about. comments carried per upvote at or above {meta['threshold']}.</div>
    <div><b class="n">NETWORK</b> — upvoted and scrolled past. attention without conversation.</div>
    <div><b class="u">UNVERIFIED</b> — surface carried no engagement data. ranked below measured items.</div>
  </div>
  <div class="sig">ARCHIVE: CHI/HMB/047 // TIME INDEX: 02:47 AM CST // DO NOT ANSWER</div>
</main>
</body>
</html>
"""

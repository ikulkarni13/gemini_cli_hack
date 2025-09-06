import json
from pathlib import Path
from datetime import datetime

def render_ascii_board(analysis: dict) -> str:
    lines = []
    lines.append("="*72)
    lines.append(" FUTURE SELF VISION BOARD ".center(72, " "))
    lines.append("="*72)
    lines.append("")
    lines.append(" THEMES ")
    lines.append("-"*72)
    for t in analysis.get("themes", [])[:6]:
        lines.append(f"• {t['name']}")
        ev = ", ".join(t.get("evidence", [])[:3])
        if ev:
            lines.append(f"   evidence: {ev}")
    lines.append("")
    lines.append(" FUTURE IDENTITIES ")
    lines.append("-"*72)
    for fi in analysis.get("future_identities", [])[:3]:
        lines.append(f"» {fi['title']}")
        lines.append(f"   {fi['why']}")
    lines.append("")
    lines.append(" AFFIRMATIONS ")
    lines.append("-"*72)
    for a in analysis.get("affirmations", [])[:6]:
        lines.append(f"✓ {a}")
    lines.append("")
    lines.append(" TODAY'S ACTION PROMPTS ")
    lines.append("-"*72)
    for ap in analysis.get("action_prompts", [])[:3]:
        lines.append(f"→ {ap}")
    lines.append("")
    return "\n".join(lines)

def render_html(analysis: dict, out_path: str = "vision-board.html"):
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>Vision Board</title>
<style>
  body {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:#0b0b10; color:#f6f6f6; margin:0; }}
  .wrap {{ max-width: 1100px; margin: 32px auto; padding: 0 20px; }}
  h1 {{ font-size: 32px; margin: 0 0 16px; }}
  .muted {{ color:#aaa; font-size: 14px; margin-bottom: 28px; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); gap:16px; }}
  .card {{ background:#14141d; border-radius:16px; padding:16px; box-shadow: 0 2px 24px rgba(0,0,0,.3); }}
  .pill {{ display:inline-block; background:#222236; color:#9cc4ff; border:1px solid #334; border-radius:999px; padding:4px 10px; font-size:12px; margin-right:6px; }}
  .section {{ margin-top: 28px; }}
  .affirm {{ font-weight:600; margin:8px 0; }}
  .small {{ font-size: 12px; color:#9a9a9a; }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Future Self Vision Board</h1>
    <div class="muted">Generated locally • {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>

    <div class="section">
      <h2>Themes</h2>
      <div class="grid">
        {''.join(theme_card(t) for t in analysis.get('themes', [])[:8])}
      </div>
    </div>

    <div class="section">
      <h2>Future Identities</h2>
      <div class="grid">
        {''.join(identity_card(fi) for fi in analysis.get('future_identities', [])[:4])}
      </div>
    </div>

    <div class="section">
      <h2>Affirmations</h2>
      <div class="grid">
        {''.join(affirm_card(a) for a in analysis.get('affirmations', [])[:8])}
      </div>
    </div>

    <div class="section">
      <h2>Today’s Action Prompts</h2>
      <div class="grid">
        {''.join(action_card(ap) for ap in analysis.get('action_prompts', [])[:4])}
      </div>
    </div>

    <p class="small section">Tip: re-run weekly to watch your board evolve as your local work changes.</p>
  </div>
</body>
</html>
"""
    Path(out_path).write_text(html, encoding="utf-8")
    return out_path

def theme_card(t):
    ev = t.get("evidence", [])[:3]
    ev_html = "".join(f'<span class="pill">{escape_html(shorten(e))}</span>' for e in ev)
    return f'<div class="card"><h3>{escape_html(t["name"])}</h3><div>{ev_html}</div></div>'

def identity_card(fi):
    return f'<div class="card"><h3>{escape_html(fi["title"])}</h3><p>{escape_html(fi["why"])}</p></div>'

def affirm_card(a):
    return f'<div class="card affirm">{escape_html(a)}</div>'

def action_card(ap):
    return f'<div class="card">→ {escape_html(ap)}</div>'

def shorten(s: str, n: int = 64) -> str:
    s = s.replace("\n"," ").strip()
    return s if len(s) <= n else s[:n-1] + "…"

def escape_html(s: str) -> str:
    return (s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

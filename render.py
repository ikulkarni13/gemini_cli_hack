import json
import shutil
import os
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file manually
def load_env_file():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    # Handle both "export KEY=VALUE" and "KEY=VALUE" formats
                    if line.startswith('export '):
                        line = line[7:]  # Remove 'export '
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"\'')

load_env_file()

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

def render_html(analysis: dict, out_path: str = "vision-board.html", source_folder: str = None, generate_ai_images: bool = False):
    # Create images directory and copy referenced images
    html_dir = Path(out_path).parent
    images_dir = html_dir / "vision_board_images"
    images_dir.mkdir(exist_ok=True)
    
    # Copy images from source folder if provided
    copied_images = {}
    if source_folder:
        source_path = Path(source_folder)
        for theme in analysis.get("themes", []):
            for evidence in theme.get("evidence", []):
                if evidence.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    src_file = source_path / evidence
                    if src_file.exists():
                        dst_file = images_dir / evidence
                        shutil.copy2(src_file, dst_file)
                        copied_images[evidence] = f"vision_board_images/{evidence}"
    
    # Generate AI images for vision scenes if requested
    ai_generated_images = {}
    if generate_ai_images:
        from image_generator import generate_single_scene_image
        import os
        
        api_key = os.environ.get("OPENAI_API_KEY")  # Use OpenAI API key for DALL-E
        if api_key:
            for i, scene in enumerate(analysis.get("vision_board_scenes", [])):
                try:
                    print(f"[ai-image] Generating image for: {scene['theme']}")
                    img = generate_single_scene_image(scene['image_description'], api_key)
                    img_filename = f"ai_vision_{i+1}_{scene['theme'].replace(' ', '_').lower()}.png"
                    img_path = images_dir / img_filename
                    img.save(img_path)
                    ai_generated_images[scene['theme']] = f"vision_board_images/{img_filename}"
                    print(f"[ai-image] Saved: {img_filename}")
                    print(f"[debug] Added to ai_generated_images: '{scene['theme']}' -> '{ai_generated_images[scene['theme']]}')")
                except Exception as e:
                    print(f"[warn] Failed to generate AI image for {scene['theme']}: {e}")
        else:
            print("[warn] GOOGLE_API_KEY not set, skipping AI image generation")
    
    # Add vision board scenes section if available
    vision_scenes_html = ""
    vision_scenes = analysis.get("vision_board_scenes", [])
    if vision_scenes:
        vision_scenes_html = f"""
    <div class="section">
      <h2>Vision Board Scenes</h2>
      <div class="grid">
        {''.join(vision_scene_card(vs, ai_generated_images) for vs in vision_scenes[:4])}
      </div>
    </div>"""

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
  .vision-card {{ background:#1a1a2e; border: 2px solid #16213e; }}
  .vision-desc {{ font-style: italic; color: #b8c5d1; margin-top: 8px; font-size: 14px; }}
  .evidence-images {{ margin-top: 12px; }}
  .evidence-img {{ max-width: 100%; height: 120px; object-fit: cover; border-radius: 8px; margin: 4px; }}
</style>
</head>
<body>
  <div class="wrap">
    <h1>Future Self Vision Board</h1>
    <div class="muted">Generated locally • {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>

    {vision_scenes_html}

    <div class="section">
      <h2>Themes</h2>
      <div class="grid">
        {''.join(theme_card(t, copied_images) for t in analysis.get('themes', [])[:8])}
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
      <h2>Today's Action Prompts</h2>
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

def theme_card(t, copied_images=None):
    if copied_images is None:
        copied_images = {}
    
    ev = t.get("evidence", [])[:3]
    
    # Separate image files from other evidence
    image_files = [e for e in ev if e.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    other_evidence = [e for e in ev if not e.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    
    # Create image HTML if we have image files
    images_html = ""
    if image_files:
        images_html = '<div class="evidence-images">'
        for img in image_files:
            # Use relative path if image was copied, otherwise show filename
            if img in copied_images:
                img_path = copied_images[img]
                images_html += f'<img src="{img_path}" alt="{escape_html(img)}" class="evidence-img" title="{escape_html(img)}">'
            else:
                # Fallback to pill if image couldn't be copied
                other_evidence.append(img)
        images_html += '</div>'
    
    # Create pills for non-image evidence
    ev_html = "".join(f'<span class="pill">{escape_html(shorten(e))}</span>' for e in other_evidence)
    
    return f'<div class="card"><h3>{escape_html(t["name"])}</h3><div>{ev_html}</div>{images_html}</div>'

def vision_scene_card(vs, ai_generated_images=None):
    if ai_generated_images is None:
        ai_generated_images = {}
    
    theme = escape_html(vs.get("theme", ""))
    success_viz = escape_html(vs.get("success_visualization", ""))
    image_desc = escape_html(vs.get("image_description", ""))
    
    # Debug output
    print(f"[debug] Looking for theme: '{vs.get('theme', '')}' in ai_generated_images")
    print(f"[debug] Available keys: {list(ai_generated_images.keys())}")
    
    # Add AI-generated image if available
    image_html = ""
    if vs.get("theme", "") in ai_generated_images:
        img_path = ai_generated_images[vs.get("theme", "")]
        image_html = f'<img src="{img_path}" alt="AI Vision: {theme}" style="width: 100%; max-height: 200px; object-fit: cover; border-radius: 8px; margin: 12px 0;">'
        print(f"[debug] Found image for theme, adding: {img_path}")
    else:
        print(f"[debug] No image found for theme: '{vs.get('theme', '')}'")
    
    return f'''<div class="card vision-card">
        <h3>{theme}</h3>
        {image_html}
        <p><strong>Success Vision:</strong> {success_viz}</p>
        <div class="vision-desc">
            <strong>Visualization:</strong> {image_desc}
        </div>
    </div>'''

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

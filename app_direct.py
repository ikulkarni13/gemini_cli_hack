import json
import argparse
import re
from utils import list_files, build_context_snippets
from gemini_direct import call_gemini_direct, themes_prompt
from render import render_ascii_board, render_html

def _shrink_for_size(items, max_chars=8000, min_per_file=60, start_per_file=120, step=20):
    """
    Trim each file's snippet so the final JSON stays under max_chars.
    Keeps structure stable for the prompt while avoiding Windows arg/STDIN slowdowns.
    """
    per_file = start_per_file
    while True:
        shrunk = [
            {
                "path": it["path"],
                "name": it["name"],
                "snippet": (it.get("snippet") or "")[:per_file],
            }
            for it in items
        ]
        s = json.dumps(shrunk, ensure_ascii=False)
        if len(s) <= max_chars or per_file <= min_per_file:
            return shrunk, s
        per_file -= step

def main():
    ap = argparse.ArgumentParser(description="Generate a future-self vision board from local files.")
    ap.add_argument("root", help="Folder to scan (e.g., ~/Documents or ./demo_data)")
    ap.add_argument("--max-files", type=int, default=80, help="Cap number of files to sample")
    ap.add_argument("--model", default="gemini-1.5-flash", help="Gemini model (e.g., gemini-1.5-flash or gemini-1.5-pro)")
    ap.add_argument("--out", default="vision-board.html", help="Output HTML file")
    ap.add_argument("--no-ascii", action="store_true", help="Skip terminal ASCII board")
    args = ap.parse_args()

    # ----- Scan & build snippets -----
    print(f"[scan] Walking: {args.root}")
    paths = list_files(args.root, max_files=args.max_files)
    print(f"[scan] Sampled files: {len(paths)}")

    print("[scan] Extracting text/metadata…")
    snippets = build_context_snippets(paths)
    print(f"[scan] Built {len(snippets)} snippets")

    # Minimal payload for the model
    compact = [{"path": s["path"], "name": s["name"], "snippet": s.get("snippet", "")} for s in snippets]

    # Fallback if nothing readable (e.g., image-only PDFs): use filenames as weak signals
    if not compact:
        print("[warn] No readable text extracted; falling back to filenames only.")
        compact = [{"path": str(p), "name": p.name, "snippet": p.stem} for p in paths]

    # Cap prompt size for snappy API calls
    compact, snippets_json = _shrink_for_size(compact, max_chars=8000)
    print(f"[gemini] Prompt chars: {len(snippets_json)}")
    print(f"[gemini] Calling model: {args.model}")

    # ----- Build prompt & call Gemini CLI -----
    prompt = themes_prompt(snippets_json)
    raw = call_gemini_direct(prompt, model=args.model)
    
    # Debug: Show what we got back
    print(f"[debug] Raw response length: {len(raw)}")
    print(f"[debug] Raw response (first 200 chars): {repr(raw[:200])}")

    # ----- Parse JSON robustly -----
    # Handle empty response
    if not raw or raw.strip() == "":
        raise RuntimeError("Gemini CLI returned empty response. Check that Gemini CLI is installed and authenticated.")
    
    # Try plain JSON first
    try:
        analysis = json.loads(raw)
    except json.JSONDecodeError:
        # Extract first {...} block in case API returns extra text
        m = re.search(r"\{.*\}", raw, flags=re.S)
        if not m:
            # Surface what we received to help debug
            raise RuntimeError("Model output was not valid JSON and no JSON block was found.\n---\n" + raw[:1000])
        analysis = json.loads(m.group(0))

    # ----- Render outputs -----
    if not args.no_ascii:
        print()
        print(render_ascii_board(analysis))

    out = render_html(analysis, out_path=args.out)
    print(f"[done] Wrote {out}")

if __name__ == "__main__":
    main()

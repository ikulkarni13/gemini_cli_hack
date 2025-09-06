# Vision Board (Local + Gemini CLI)

**What it does**  
Scans a local folder, samples filenames/snippets, and asks Gemini to infer your strongest themes, future identities, and concise affirmations. Outputs:
- Terminal “ASCII board”
- `vision-board.html` with clean cards

**Why it matters**  
It turns your *real work-in-progress* into motivation: a personal, evolving vision board grounded in your actual files.

**How to run**
```bash
python -m venv .venv && source .venv/bin/activate
# Ensure Gemini CLI is installed + authed
python app.py ~/Documents --max-files 80 --out vision-board.html
open vision-board.html  # macOS; use xdg-open on Linux

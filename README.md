# Vision Board (Local + Gemini CLI)

**What it does**  
Scans a local folder, samples filenames/snippets, and asks Gemini CLI to infer your strongest themes, future identities, and concise affirmations. Outputs:
- Terminal "ASCII board"
- `vision-board.html` with clean cards

**Prerequisites**
1. Install Gemini CLI: `npm install -g @google/generative-ai-cli`
2. Authenticate: `gemini auth login`

**Quick Start**  
```bash
git clone <this-repo>
cd vision-board
pip install -r requirements.txt
```

Windows:
```bash
python -m venv .venv && .venv\Scripts\activate
python app_direct.py ~/Documents --max-files 80 --out vision-board.html
# Open vision-board.html in your browser
```

Mac:
run this in cmd export GOOGLE_API_KEY='your api key'
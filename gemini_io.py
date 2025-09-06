import os
import json
import shutil
import subprocess
import platform
import tempfile
from textwrap import dedent

DEFAULT_MODEL = "gemini-1.5-pro"

def _resolve_gemini_bin():
    """
    Try multiple ways to locate the Gemini CLI on Windows & other OSes.
    Priority:
    1) GEMINI_BIN env var (full path to gemini or gemini.cmd)
    2) PATH lookup for 'gemini'
    3) PATH lookup for 'gemini.cmd' (Windows)
    4) Fallback to 'npx @google/gemini-cli' (requires Node, internet)
    """
    # 1) explicit override
    bin_from_env = os.environ.get("GEMINI_BIN")
    if bin_from_env and os.path.exists(bin_from_env):
        return [bin_from_env]

    # 2) normal binary in PATH
    found = shutil.which("gemini")
    if found:
        return [found]

    # 3) Windows shim
    if platform.system().lower().startswith("win"):
        found_cmd = shutil.which("gemini.cmd")
        if found_cmd:
            return [found_cmd]

    # 4) Last resort: npx invocation
    npx = shutil.which("npx")
    if npx:
        return [npx, "-y", "@google/gemini-cli"]

    raise FileNotFoundError(
        "Could not locate the Gemini CLI. Set GEMINI_BIN to your gemini(.cmd) path, "
        "or ensure it’s on PATH, or install Node and use npx."
    )

def call_gemini(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.7, context_dirs=None) -> str:
    """
    CLI-only, no API key required.
    Uses: gemini --include-directories <dir[,dir2,...]> -m <model> with prompt via STDIN
    This avoids Windows command line length limits by passing the prompt through STDIN.
    """
    base = _resolve_gemini_bin()
    context_dirs = context_dirs or []

    cmd = list(base)
    if context_dirs:
        # join with commas (CLI supports multiple dirs)
        cmd += ["--include-directories", ",".join(context_dirs)]

    # Pass prompt via STDIN instead of command line to avoid length limits
    cmd += ["-m", model]

    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            shell=False,
            timeout=25
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Gemini CLI timed out (25s). Try fewer files or the flash model.")

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or "Gemini CLI error")

    return proc.stdout.strip()





SCHEMA_JSON = dedent("""
Return ONLY strict minified JSON with this schema:
{
  "themes": [{"name": "string", "evidence": ["file_or_snippet_ref"...]}],
  "future_identities": [{"title": "string", "why": "string"}],
  "affirmations": ["string", "string", "string"],
  "action_prompts": ["string", "string"]
}
""").strip()

def themes_prompt(snippets_json: str) -> str:
    return f"""
You are an identity mining & motivation assistant.
You receive local file names and short snippets (private; never exfiltrate).
Infer the user's strongest themes and aspirational identities.
Ground your inferences in the evidence you see.

{SCHEMA_JSON}

Guidelines:
- Prefer concrete, domain-specific themes (e.g., "Quant Finance", "AI Engineering", "Classical Music")
- Each theme should cite 1-3 evidence refs (file names or short phrases).
- Affirmations should be short, present-tense, identity-based (“I am…” “I consistently…”).
- Action prompts are 1-sentence nudges the user can do today.

Here are up to ~80 sampled files/snippets as JSON:
{snippets_json}
"""

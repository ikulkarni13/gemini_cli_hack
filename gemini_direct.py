import os
import json
import subprocess
import tempfile
from textwrap import dedent

DEFAULT_MODEL = "gemini-2.5-flash"

def call_gemini_cli(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Call Gemini using the official Gemini CLI.
    Requires gemini CLI to be installed and authenticated.
    """
    try:
        # Build the gemini CLI command using -p flag for prompt
        cmd = [
            'gemini',
            '--model', model,
            '--prompt', prompt
        ]
        
        print(f"[debug] Calling Gemini CLI with model: {model}")
        print(f"[debug] Command: gemini --model {model} --prompt [PROMPT_TEXT]")
        
        # Execute the CLI command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Debug output
        print(f"[debug] CLI exit code: {result.returncode}")
        print(f"[debug] CLI stdout length: {len(result.stdout) if result.stdout else 0}")
        print(f"[debug] CLI stderr length: {len(result.stderr) if result.stderr else 0}")
        if result.stderr:
            print(f"[debug] CLI stderr: {result.stderr[:500]}")
        if result.stdout:
            print(f"[debug] CLI stdout preview: {result.stdout[:200]}")
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            if "not found" in error_msg or "command not found" in error_msg:
                raise RuntimeError(
                    "Gemini CLI not found. Please install it:\n"
                    "1. Install: npm install -g @google/generative-ai-cli\n"
                    "2. Authenticate: gemini auth login\n"
                    "3. Or follow: https://github.com/google/generative-ai-cli"
                )
            raise RuntimeError(f"Gemini CLI failed (exit {result.returncode}): {error_msg}")
        
        output = result.stdout.strip()
        if not output:
            raise RuntimeError("Gemini CLI returned empty output")
            
        return output
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Gemini CLI call timed out after 60 seconds")
    except FileNotFoundError:
        raise RuntimeError(
            "Gemini CLI not found. Please install it:\n"
            "1. Install: npm install -g @google/generative-ai-cli\n"
            "2. Authenticate: gemini auth login\n"
            "3. Or follow: https://github.com/google/generative-ai-cli"
        )
    except Exception as e:
        raise RuntimeError(f"Unexpected error calling Gemini CLI: {e}")

# Keep the old function name for compatibility
def call_gemini_direct(prompt: str, model: str = DEFAULT_MODEL, api_key: str = None) -> str:
    """
    Wrapper for backward compatibility - now uses CLI instead of direct API.
    """
    return call_gemini_cli(prompt, model)

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
- Affirmations should be short, present-tense, identity-based ("I am…" "I consistently…").
- Action prompts are 1-sentence nudges the user can do today.

Here are up to ~80 sampled files/snippets as JSON:
{snippets_json}
"""

import os
import json
import requests
from textwrap import dedent

DEFAULT_MODEL = "gemini-1.5-flash"

def call_gemini_direct(prompt: str, model: str = DEFAULT_MODEL, api_key: str = None) -> str:
    """
    Direct API call to Google AI Studio Gemini API.
    Requires GOOGLE_API_KEY environment variable or api_key parameter.
    """
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    # Try to load from .env file if not found in environment
    if not api_key:
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break
        except FileNotFoundError:
            pass
    
    if not api_key:
        raise RuntimeError(
            "No API key found. Please:\n"
            "1. Go to https://makersuite.google.com/app/apikey\n"
            "2. Create a new API key\n"
            "3. Set it as environment variable: $env:GOOGLE_API_KEY='your-key-here'\n"
            "Or create a .env file with GOOGLE_API_KEY=your-key-here"
        )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        }
    }
    
    try:
        print(f"[debug] Calling Gemini API directly with model: {model}")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            return content.strip()
        else:
            raise RuntimeError(f"Unexpected API response format: {result}")
            
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")
    except KeyError as e:
        raise RuntimeError(f"Unexpected response format, missing key: {e}. Response: {result}")

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

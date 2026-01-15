import json
import subprocess

SYSTEM_PROMPT = """
You are an assistant that extracts structured filters from real estate queries.
Return ONLY valid JSON.
Fields:
- bhk (int or null)
- max_price (number in rupees or null)
- require_gym (boolean)
"""

def parse_with_llm(user_query: str):
    prompt = f"""
{SYSTEM_PROMPT}

Query:
{user_query}
"""

    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt,
        text=True,
        capture_output=True
    )

    try:
        return json.loads(result.stdout)
    except Exception:
        return {}

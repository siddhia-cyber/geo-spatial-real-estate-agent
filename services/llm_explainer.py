import subprocess
from services.logger import get_logger
logger = get_logger(__name__)


def explain_results(user_query, results):
    try:
        count = len(results)

        # Build grounded summary (facts only)
        summary = "\n".join([
    f"{r['bhk']} BHK in {r['locality']} priced at Rs {r['price']} with area {r['area_sqft']} square feet"
    for r in results[:3]
])

        prompt = f"""
 You are generating a natural language explanation for real estate search results.
        IMPORTANT CONTEXT:
- All properties belong to the city of Mumbai.



User query:
{user_query}

Number of matching properties: {count}

Matching properties (facts only, do not change wording):
{summary}

STRICT RULES:
- Write in plain English sentences.
- DO NOT use markdown, bullet points, symbols, or asterisks.
- DO NOT use ** or formatting of any kind.
- ALWAYS mention the exact locality name as provided.
- ALWAYS mention the exact BHK count.
- ALWAYS mention the price in rupees.
- Mention amenities only if they exist.
- NEVER use generic words like "location", "area", or "property type".
- NEVER invent or assume information.
- If there is one result, write in singular.
- Keep the explanation concise (2–3 sentences).
- NEVER invent or assume information.
- ALWAYS use the locality and city exactly as provided.


Now write the explanation.
"""
        logger.info("Generating explanation using LLM")

        result = subprocess.run(
            ["ollama", "run", "llama3.2"],
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",
            timeout=60
        )

        output = result.stdout.strip()

        if not output:
            logger.warning("LLM returned empty output")


            return "Explanation could not be generated."
        
        logger.info("LLM explanation generated successfully")
        return output

    except Exception:
        logger.error("LLM explanation failed", exc_info=True)

        return "Explanation could not be generated."


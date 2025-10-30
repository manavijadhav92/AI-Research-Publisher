# services/analyzer.py
from services.bedrock_client import invoke_mistral
import json, textwrap

def build_analysis_prompt(topic, top_papers):
    # top_papers: list of dicts {title, abstract, url, year}
    docs = []
    for i,p in enumerate(top_papers, 1):
        docs.append(f"Paper {i} Title: {p['title']}\nAbstract: {p['abstract']}\nURL: {p.get('url','')}\n")
    docs_block = "\n\n".join(docs)
    prompt = f"""
You are an expert academic research assistant.

TASK: Using the papers below about "{topic}", produce JSON with these fields:
- summary: a concise 3-4 sentence synthesis of the current state-of-the-art.
- limitations: an array of up to 6 bullet items (each 1-sentence) describing common limitations, open gaps, or weaknesses across these papers.
- innovations: an array of 3 proposed novel research ideas (each must include: title, summary (1-2 sentences), a short experimental validation plan (1 sentence), and one metric to evaluate).

Output EXACTLY valid JSON with these keys: summary, limitations, innovations. Do not add extra commentary.

PAPERS:
{docs_block}

Return only JSON.
"""
    return textwrap.dedent(prompt)

def analyze_topic(topic, papers, top_k=5):
    top_papers = papers[:top_k]
    prompt = build_analysis_prompt(topic, top_papers)
    raw = invoke_mistral(prompt, max_tokens=1200, temp=0.2)
    # raw may be {"text":"..."} or a dict or plain string; normalize:
    text = raw.get("text") if isinstance(raw, dict) else raw
    if isinstance(text, dict):
        return text
    elif isinstance(text, str):
        # model should return JSON string — try parse
        try:
            return json.loads(text)
        except Exception as e:
            # fallback: wrap raw text in diagnostic structure
            return {"error": "parse_failed", "raw": text}

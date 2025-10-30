# services/fetch_papers.py
import requests
import time

S2_BASE = "https://api.semanticscholar.org/graph/v1"

def search_semantic_scholar(topic, limit=8):
    """Return list of papers: {'title','abstract','url','year','authors'}"""
    q = requests.utils.quote(topic)
    fields = "title,abstract,url,year,authors"
    url = f"{S2_BASE}/paper/search?query={q}&limit={limit}&fields={fields}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json().get("data", [])
    papers = []
    for p in data:
        if p.get("abstract"):
            papers.append({
                "title": p.get("title"),
                "abstract": p.get("abstract"),
                "url": p.get("url"),
                "year": p.get("year"),
                "authors": [a.get("name") for a in p.get("authors", [])][:5]
            })
    # small delay to keep polite to the API
    time.sleep(0.5)
    return papers

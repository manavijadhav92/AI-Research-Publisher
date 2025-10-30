# services/embeddings.py
import boto3, json
import numpy as np
import os

REGION = os.getenv("AWS_REGION", "us-east-1")
EMB_MODEL = "amazon.titan-embed-text-v1"  # confirm exact modelId in your account

client = boto3.client("bedrock-runtime", region_name=REGION)

def embed_text(text):
    body = {"inputText": text}
    resp = client.invoke_model(modelId=EMB_MODEL, body=json.dumps(body).encode("utf-8"))
    raw = json.loads(resp["body"].read().decode())
    # response format may vary; adjust if different. Look for 'embeddings' or 'embedding'
    emb = raw.get("embeddings") or raw.get("embedding") or raw.get("vector")
    return np.array(emb)

def rank_papers_by_relevance(query, papers):
    q_emb = embed_text(query)
    scores = []
    for p in papers:
        a_emb = embed_text(p["abstract"][:2000])
        sim = float(np.dot(q_emb, a_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(a_emb)))
        scores.append((sim, p))
    scores.sort(reverse=True, key=lambda x: x[0])
    return [p for s,p in scores]

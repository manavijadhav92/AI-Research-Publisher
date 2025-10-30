import os
import json
import uuid
import boto3
import requests
from fpdf import FPDF
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from botocore.exceptions import ClientError

# =========================================
# 🔧 CONFIGURATION
# =========================================
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "my-research-papers")
S3_PRESIGN_EXPIRY = int(os.getenv("S3_PRESIGN_EXPIRY", 86400))

# AWS Clients
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)

app = FastAPI(title="AI Research Paper Publisher")

# =========================================
# 📘 MODELS
# =========================================
class PromptRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    question: str
    context: str

# =========================================
# 🏠 HOME ROUTE
# =========================================
@app.get("/")
def root():
    return {"message": "✅ AI Research Paper Publisher running."}

# =========================================
# 📚 FETCH PAPERS FROM ARXIV
# =========================================
def fetch_arxiv(topic: str, max_results: int = 3):
    query = requests.utils.quote(topic)
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()

    entries = r.text.split("<entry>")[1:]
    papers = []
    for entry in entries:
        try:
            title = entry.split("<title>")[1].split("</title>")[0].strip()
            summary = entry.split("<summary>")[1].split("</summary>")[0].strip()
            link = entry.split("<id>")[1].split("</id>")[0].strip() if "<id>" in entry else ""
            papers.append({"source": "arXiv", "title": title, "summary": summary, "url": link})
        except Exception:
            continue
    return papers

# =========================================
# 🧠 BUILD IEEE PROMPT
# =========================================
def build_ieee_prompt(topic: str, papers: list):
    docs = "\n\n".join([
        f"Title: {p['title']}\nAbstract: {p['summary']}\nURL: {p.get('url','')}"
        for p in papers
    ])
    prompt = f"""
You are an expert academic writer. Using the papers below about "{topic}", generate a well-structured IEEE-style research paper draft.
Follow these sections strictly and label each section clearly:
Abstract (100–200 words), Keywords (4–6 words), Introduction, Literature Review, Methodology, Results and Discussion, Conclusion, References.

Papers:
{docs}

Important:
- Use an academic tone and coherent paragraphs.
- Highlight limitations and future work.
- If references are not exact, include plausible citation placeholders in References.
Return only the paper text (with clear section headers).
"""
    return prompt

# =========================================
# 🤖 CALL AWS BEDROCK MODEL
# =========================================
def call_bedrock_model(prompt_text: str, model_id: str = "mistral.mistral-7b-instruct-v0:2", max_tokens: int = 900):
    body = {"prompt": prompt_text, "max_tokens": max_tokens, "temperature": 0.2}
    resp = bedrock.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )
    raw = resp["body"].read().decode("utf-8")
    try:
        parsed = json.loads(raw)
        if "outputs" in parsed:
            return "\n\n".join([o.get("text") or o.get("outputText", "") for o in parsed["outputs"]])
        return parsed.get("text", raw)
    except Exception:
        return raw

# =========================================
# 📄 SAVE AS PDF
# =========================================
def save_text_as_pdf(text: str, filename: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, text)
    pdf.output(filename)
    return filename

# =========================================
# ☁️ UPLOAD TO S3
# =========================================
def upload_file_to_s3(local_path: str, bucket: str, object_name: str):
    try:
        s3.upload_file(local_path, bucket, object_name)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': object_name},
        ExpiresIn=S3_PRESIGN_EXPIRY
    )

# =========================================
# 🧾 RESEARCH ENDPOINT
# =========================================
@app.post("/research/")
def generate_research(data: PromptRequest):
    topic = data.prompt.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    papers = fetch_arxiv(topic)
    if not papers:
        papers = [{"source": "none", "title": topic, "summary": ""}]

    prompt_text = build_ieee_prompt(topic, papers)
    ai_text = call_bedrock_model(prompt_text)

    unique_id = uuid.uuid4().hex[:8]
    safe_title = "".join(c if c.isalnum() or c in (" ", "_") else "_" for c in topic).strip().replace(" ", "_")
    filename = f"{safe_title}_{unique_id}.pdf"
    local_path = f"/tmp/{filename}" if os.name != 'nt' else filename

    save_text_as_pdf(ai_text, local_path)
    s3_key = f"generated/{filename}"
    s3_url = upload_file_to_s3(local_path, S3_BUCKET, s3_key)

    return {
        "topic": topic,
        "papers_found": len(papers),
        "papers": papers,
        "s3_url": s3_url,
        "generated_at": datetime.utcnow().isoformat(),
        "filename": filename,
        "ai_text": ai_text
    }

# =========================================
# 💬 CHATBOT ENDPOINT
# =========================================
@app.post("/chatbot/")
def chatbot(req: ChatRequest):
    try:
        question = req.question
        context = req.context
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer in IEEE academic tone."

        # Temporary mock answer (we’ll integrate Bedrock next)
        answer = f"This is an AI-generated answer for: '{question}' based on provided context."

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================================
# 🗂️ HISTORY ENDPOINT
# =========================================
@app.get("/history/")
def list_pdfs():
    """List generated research PDFs from S3."""
    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="generated/")
    if "Contents" not in response:
        return {"files": []}

    files = [{
        "file_name": obj["Key"],
        "last_modified": str(obj["LastModified"]),
        "url": f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"
    } for obj in response["Contents"]]

    return {"files": sorted(files, key=lambda x: x["last_modified"], reverse=True)}

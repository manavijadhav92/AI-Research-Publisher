# services/bedrock_client.py
import boto3, json, os
REGION = os.getenv("AWS_REGION", "us-east-1")
client = boto3.client("bedrock-runtime", region_name=REGION)

def invoke_mistral(prompt, max_tokens=900, temp=0.2):
    body = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temp}
    resp = client.invoke_model(
        modelId="mistral.mistral-7b-instruct-v0:2",
        body=json.dumps(body).encode("utf-8")
    )
    raw = resp['body'].read().decode('utf-8')
    # raw could be a JSON string or plain text; try parse safely:
    try:
        return json.loads(raw)
    except:
        return {"text": raw}

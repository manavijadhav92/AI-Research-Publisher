# streamlit_app.py
import streamlit as st
import requests
import json
from datetime import datetime
import base64

# ==============================
# 🎨 Streamlit Config
# ==============================
st.set_page_config(
    page_title="AI Research Paper Publisher",
    page_icon="📘",
    layout="wide"
)

# ==============================
# 🔧 Configuration
# ==============================
DEFAULT_BACKEND = "http://127.0.0.1:8000"
RESEARCH_ENDPOINT = "/research/"
CHATBOT_ENDPOINT = "/chatbot/"
HISTORY_ENDPOINT = "/history/"

# ==============================
# 🔍 Helper Functions
# ==============================
def post_research(topic: str, backend: str):
    url = backend.rstrip("/") + RESEARCH_ENDPOINT
    payload = {"prompt": topic}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()

def post_chat(question: str, context: str, backend: str):
    url = backend.rstrip("/") + CHATBOT_ENDPOINT
    payload = {"question": question, "context": context}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()

def get_history(backend: str):
    url = backend.rstrip("/") + HISTORY_ENDPOINT
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def download_link(text: str, filename: str, label: str = "📥 Download"):
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'
    return href

def pretty_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==============================
# 🧭 Sidebar
# ==============================
with st.sidebar:
    st.title("⚙️ Settings")
    backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND)
    st.caption("Ensure your FastAPI backend is running.")
    st.divider()

    st.subheader("🧠 Quick Topics")
    if st.button("AI in Healthcare"):
        st.session_state["topic"] = "AI in healthcare"
    if st.button("Machine Learning in Drug Discovery"):
        st.session_state["topic"] = "Machine learning in drug discovery"
    if st.button("Quantum Computing in Security"):
        st.session_state["topic"] = "Quantum computing in cybersecurity"

    st.divider()
    st.markdown("**👩‍💻 Created by Manavi Jadhav \n, Gayatri Gambhire\n, Abhijeeta Sagat\n**")

# ==============================
# 🏠 Main Tabs
# ==============================
st.title("📘 AI Research Paper Publisher")
tabs = st.tabs(["🧾 Generate Paper", "💬 Chat Assistant", "🗂️ History"])

# ==============================
# 🧾 TAB 1: GENERATE PAPER
# ==============================
with tabs[0]:
    topic = st.text_input("Enter your research topic:", value=st.session_state.get("topic", ""))
    generate_btn = st.button("🚀 Generate IEEE Paper", type="primary")

    if generate_btn:
        if not topic.strip():
            st.warning("⚠️ Please enter a topic.")
            st.stop()

        st.info("⏳ Fetching research papers and generating IEEE-style paper...")
        try:
            response = post_research(topic, backend_url)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request failed: {e}")
            st.stop()

        st.success("✅ Research paper generated successfully!")
        st.markdown("---")

        # Store last summary for chatbot
        st.session_state["last_summary"] = response

        # ---- Display Results ----
        st.subheader(f"📖 Topic: {topic}")
        st.markdown(f"**Generated on:** {pretty_datetime()}")
        st.divider()

        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown("### 🔍 Research Papers Found")
            papers = response.get("papers", [])
            if not papers:
                st.info("No papers found. Try a different keyword.")
            else:
                for i, paper in enumerate(papers, 1):
                    with st.expander(f"📄 {i}. {paper.get('title', 'Untitled')}"):
                        st.markdown(f"**Source:** {paper.get('source', 'N/A')}")
                        if paper.get("url"):
                            st.markdown(f"[🔗 Read Paper]({paper['url']})")
                        st.markdown(f"**Summary:** {paper.get('summary', '')}")

        with col2:
            st.markdown("### 🤖 IEEE Paper Summary")
            summary_text = response.get("ai_text", "")
            filename = response.get("filename", "paper.pdf")
            s3_url = response.get("s3_url", "")

            if summary_text.strip():
                st.text_area("Generated Paper Content", summary_text, height=400)
                st.markdown(download_link(summary_text, f"{topic}_summary.txt"), unsafe_allow_html=True)
            else:
                st.info("No summary text received.")

            if s3_url:
                st.markdown("---")
                st.markdown("### 📄 Download IEEE PDF")
                st.success("Your paper has been uploaded to S3.")
                st.markdown(f"[📘 View PDF in S3]({s3_url})")

# =============================
# 💬 TAB 2: CHAT ASSISTANT
# =============================
with tabs[1]:
    st.subheader("Ask questions about your last summary")
    if "last_summary" not in st.session_state:
        st.info("⚠️ No summary generated yet. Please generate one first.")
    else:
        context = json.dumps(st.session_state["last_summary"])
        question = st.text_input("Ask a question (e.g., 'Summarize related works of paper #2')")
        if st.button("Ask"):
            with st.spinner("Thinking..."):
                try:
                    res = post_chat(question, context, backend_url)
                    answer = res.get("answer", "No answer found.")
                    st.markdown(f"**🧠 Answer:** {answer}")
                except Exception as e:
                    st.error(f"❌ Chatbot error: {e}")

# =============================
# 🗂️ TAB 3: HISTORY DASHBOARD
# =============================
with tabs[2]:
    st.subheader("📂 Previously Generated Papers (from S3)")
    try:
        history = get_history(backend_url)
        files = history.get("files", [])
        if not files:
            st.info("No research papers found in S3 yet.")
        else:
            for f in files:
                with st.expander(f"📘 {f['file_name']}"):
                    st.markdown(f"**Uploaded:** {f['last_modified']}")
                    st.markdown(f"[🔗 View PDF]({f['url']})")
    except Exception as e:
        st.error(f"❌ Failed to fetch S3 history: {e}")

# ------------------------------
# 🧾 Footer
# ------------------------------
st.markdown("---")
st.caption(f"🕒 Last updated: {pretty_datetime()} | Backend: {DEFAULT_BACKEND}")

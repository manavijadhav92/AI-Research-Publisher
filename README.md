# 🧠 AI Research Paper Publisher

An AI-powered web application that automatically generates **IEEE-style research papers** from user prompts using **AWS Bedrock**, stores them securely in **Amazon S3**, and provides an **interactive chatbot** for exploring generated papers.

---

## 🚀 Features

- ✨ Generate academic research papers in IEEE format.
- 📄 Automatically save generated papers as PDFs.
- ☁️ Upload and retrieve papers from AWS S3.
- 💬 Chatbot assistant for summarizing or querying generated research.
- 🕓 View history of all previously generated papers.

---

## 🧰 Tech Stack

| Component | Technology Used |
|------------|----------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| AI Model | AWS Bedrock (Mistral 7B) |
| Database | Amazon S3 |
| PDF Generation | FPDF |
| Cloud | AWS EC2, S3, Bedrock |
| Language | Python 3.10+ |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/ManaviJadhav/ai_research_publisher.git
cd ai_research_publisher


2️⃣ Create a Virtual Environment
conda create -n ai_research python=3.10
conda activate ai_research

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure AWS Credentials

Create a .env file in the project root:
 
   AWS_REGION=us-east-1
   S3_BUCKET=your-s3-bucket-name
   S3_PRESIGN_EXPIRY=86400

Make sure you have run:
   aws configure


Run the Application
Start FastAPI Backend: uvicorn main:app --host 0.0.0.0 --port 8000

Start Streamlit Frontend
Start Frontend: streamlit run streamlit_app.py

🧾 Project Folder Structure

ai_research_publisher/
│
├── main.py                # FastAPI backend with Bedrock + S3 logic
├── streamlit_app.py       # Streamlit frontend for user interaction
├── requirements.txt       # Dependencies
├── .env                   # AWS credentials and configuration
└── README.md              # Project documentation




Author

Manavi Jadhav
MCA Student | AI & Cloud Enthusiast
manavijd26@gmail.com
https://www.linkedin.com/in/manavi-jadhav-92117a290/


Demo Of the Project -

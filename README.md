# 🧠 AI Resume Assistant

An AI-powered resume analysis tool built with **FastAPI**, **Streamlit**, and **Groq AI**.

## ✨ Features
- 📄 **Resume Analysis** — Get instant AI feedback, ATS score & improvement tips
- 📊 **JD Comparison** — Compare your resume against a job description with match score
- 🎯 **Interview Prep** — Get AI-generated tailored interview questions

## 🚀 How to Run

### Step 1 — Clone the repository
```bash
git clone https://github.com/nikita-pawar487/AI-Resume-Assistant.git
cd AI-Resume-Assistant
```

### Step 2 — Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install fastapi uvicorn streamlit pdfminer.six python-docx plotly groq
```

### Step 4 — Get a free Groq API key
👉 [console.groq.com](https://console.groq.com) → Sign up → Create API Key

### Step 5 — Set your API key
```bash
$env:GROQ_API_KEY="your_groq_key_here"
```

### Step 6 — Run the backend
```bash
uvicorn main:app --reload
```

### Step 7 — Open a new terminal and run the frontend
```bash
venv\Scripts\activate
streamlit run app.py
```

### Step 8 — Open your browser
Go to 👉 http://localhost:8501

## 🛠️ Tech Stack
- **Frontend** — Streamlit
- **Backend** — FastAPI
- **AI** — Groq (LLaMA 3.3 70B)
- **PDF Parsing** — pdfminer.six
- **Charts** — Plotly

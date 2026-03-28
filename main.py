from fastapi import FastAPI, UploadFile, File, Form
from pdfminer.high_level import extract_text
import docx
import re
import os
import json
from groq import Groq

app = FastAPI()

# ── Configure Groq ────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


# ── Helper: Extract text from uploaded file ───────────────────────────────────
def extract_resume_text(file) -> str:
    if file.filename.endswith(".pdf"):
        return extract_text(file.file)
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""


# ── Helper: Call Groq and parse JSON response ─────────────────────────────────
def ask_groq(prompt: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "AI Resume Assistant is running!"}


# ── 1. Resume Analysis ────────────────────────────────────────────────────────
@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    text = extract_resume_text(file)
    if not text:
        return {"error": "Unsupported file format or empty file"}

    prompt = f"""
You are an expert resume reviewer. Analyze the following resume and return ONLY a valid JSON object with no extra text or markdown.

Resume:
\"\"\"{text[:3000]}\"\"\"

Return this exact JSON structure with real analysis based on the resume above:
{{
  "overall_score": "82/100",
  "ats_score": "75%",
  "sections_count": 5,
  "strengths": [
    "Strong technical skills section",
    "Clear education background",
    "Good project descriptions"
  ],
  "improvements": [
    "Add a professional summary",
    "Quantify achievements with numbers",
    "Add LinkedIn or GitHub links"
  ],
  "feedback": "This is a well-structured resume with clear sections. The candidate shows strong technical ability but could improve by adding measurable achievements and a professional summary."
}}

Analyze the actual content and return realistic values. Return ONLY the JSON, nothing else.
"""
    try:
        result = ask_groq(prompt)
        return result
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}


# ── 2. JD Comparison ─────────────────────────────────────────────────────────
@app.post("/compare-with-jd/")
async def compare_with_jd(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    text = extract_resume_text(file)
    if not text:
        return {"error": "Unsupported file format or empty file"}

    prompt = f"""
You are an expert recruiter. Compare the resume against the job description and return ONLY a valid JSON object with no extra text or markdown.

Resume:
\"\"\"{text[:2000]}\"\"\"

Job Description:
\"\"\"{job_description[:2000]}\"\"\"

Return this exact JSON structure:
{{
  "match_score_percentage": 72,
  "present_skills": ["Python", "SQL", "Communication", "Teamwork"],
  "missing_technical_skills": ["Docker", "AWS", "Kubernetes"],
  "missing_soft_skills": ["Leadership", "Project Management"],
  "summary": "The candidate matches 72% of the job requirements. Strong in core programming but lacks cloud experience."
}}

Rules:
- match_score_percentage must be a realistic number between 0 and 100
- present_skills = skills found in BOTH resume and JD
- missing_technical_skills = technical skills in JD but NOT in resume
- missing_soft_skills = soft skills in JD but NOT in resume
- Be thorough and realistic
- Return ONLY the JSON, nothing else.
"""
    try:
        result = ask_groq(prompt)
        return result
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}


# ── 3. Interview Questions ────────────────────────────────────────────────────
@app.post("/generate-questions/")
async def generate_questions(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    text = extract_resume_text(file)
    if not text:
        return {"error": "Unsupported file format or empty file"}

    prompt = f"""
You are an expert interview coach. Generate tailored interview questions based on the resume and job description. Return ONLY a valid JSON object with no extra text or markdown.

Resume:
\"\"\"{text[:2000]}\"\"\"

Job Description:
\"\"\"{job_description[:2000]}\"\"\"

Return this exact JSON structure:
{{
  "questions": [
    {{
      "category": "Technical Skills",
      "question": "Can you walk us through a project where you used Python?"
    }},
    {{
      "category": "Technical Skills",
      "question": "How have you used SQL to solve complex data problems?"
    }},
    {{
      "category": "Behavioural",
      "question": "Tell me about a time you had to meet a tight deadline."
    }},
    {{
      "category": "Behavioural",
      "question": "Describe a situation where you worked with a difficult team member."
    }},
    {{
      "category": "Role Specific",
      "question": "How would you approach building a scalable REST API?"
    }},
    {{
      "category": "Role Specific",
      "question": "What strategies would you use to ensure code quality?"
    }},
    {{
      "category": "Culture Fit",
      "question": "What motivates you to work in this industry?"
    }},
    {{
      "category": "Culture Fit",
      "question": "Where do you see yourself in 5 years?"
    }}
  ]
}}

Generate exactly 10 diverse, thoughtful questions tailored to this specific resume and job description.
Return ONLY the JSON, nothing else.
"""
    try:
        result = ask_groq(prompt)
        return result
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}
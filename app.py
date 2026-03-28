import streamlit as st
import plotly.graph_objects as go
from pdfminer.high_level import extract_text
import docx
import re
import os
import json
from groq import Groq
import io

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Groq Client ───────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6f0;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

.hero {
    background: linear-gradient(135deg, #1a0533 0%, #0d1b4b 50%, #0a2a1a 100%);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 20px;
    padding: 3rem 3.5rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem;
    letter-spacing: -1px;
}
.hero p {
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 300;
    margin: 0;
    max-width: 560px;
}
.hero-badge {
    display: inline-block;
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.35);
    color: #a78bfa;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 50px;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 10px;
    color: #64748b;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0.6rem 1.4rem;
    border: none;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #059669) !important;
    color: white !important;
    font-weight: 600;
}
.stTabs [data-baseweb="tab-border"] { display: none; }

[data-testid="stFileUploader"] {
    background: rgba(139,92,246,0.06);
    border: 2px dashed rgba(139,92,246,0.3);
    border-radius: 16px;
    padding: 1rem;
}

.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #059669 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.7rem 2rem;
    width: 100%;
    transition: all 0.25s;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124,58,237,0.4);
}

.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-accent { border-left: 3px solid #7c3aed; }

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.8rem !important; }
[data-testid="stMetricValue"] { color: #a78bfa !important; font-family: 'Syne', sans-serif !important; }

.skill-tag {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0.25rem;
}
.skill-missing-tech {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.3);
    color: #fca5a5;
}
.skill-missing-soft {
    background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.3);
    color: #fde68a;
}
.skill-present {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    color: #6ee7b7;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.q-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(139,92,246,0.15);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.75rem;
    position: relative;
    padding-left: 3.5rem;
}
.q-number {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #7c3aed, #059669);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    color: white;
}

hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Helper: Extract text ──────────────────────────────────────────────────────
def extract_resume_text(file) -> str:
    if file.name.endswith(".pdf"):
        return extract_text(io.BytesIO(file.read()))
    elif file.name.endswith(".docx"):
        doc = docx.Document(io.BytesIO(file.read()))
        return "\n".join([para.text for para in doc.paragraphs])
    return ""


# ── Helper: Call Groq ─────────────────────────────────────────────────────────
def ask_groq(prompt: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)


# ── Helper: Donut Chart ───────────────────────────────────────────────────────
def make_donut_chart(score: float) -> go.Figure:
    color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
    fig = go.Figure(go.Pie(
        values=[score, 100 - score],
        hole=0.72,
        marker_colors=[color, "rgba(255,255,255,0.05)"],
        textinfo="none",
        hoverinfo="skip",
    ))
    fig.add_annotation(text=f"<b>{score:.0f}%</b>", x=0.5, y=0.55, showarrow=False,
                       font=dict(size=32, color=color, family="Syne"))
    fig.add_annotation(text="Match", x=0.5, y=0.38, showarrow=False,
                       font=dict(size=13, color="#94a3b8", family="DM Sans"))
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220)
    return fig


# ── Helper: Skills Bar Chart ──────────────────────────────────────────────────
def make_skills_bar(present, missing_tech, missing_soft) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=["Present", "Missing Technical", "Missing Soft"],
        y=[len(present), len(missing_tech), len(missing_soft)],
        marker_color=["#10b981", "#ef4444", "#f59e0b"],
        text=[len(present), len(missing_tech), len(missing_soft)],
        textposition="outside",
        textfont=dict(color="#e2e8f0", family="DM Sans"),
        width=0.4,
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(t=20, b=10, l=10, r=10), height=220,
                      yaxis=dict(showgrid=False, visible=False),
                      xaxis=dict(tickfont=dict(color="#94a3b8", family="DM Sans")))
    return fig


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ AI Powered</div>
    <h1>Resume Assistant</h1>
    <p>Upload your resume, paste a job description, and let AI guide you to your dream role — with smart analysis, skill gap detection & interview prep.</p>
</div>
""", unsafe_allow_html=True)


# ── Upload & JD ───────────────────────────────────────────────────────────────
col_up, col_jd = st.columns([1, 1], gap="large")

with col_up:
    st.markdown('<div class="section-title">📄 Your Resume</div>', unsafe_allow_html=True)
    resume = st.file_uploader("", type=["pdf", "docx"], label_visibility="collapsed")
    if resume:
        st.success(f"✅ **{resume.name}** uploaded successfully")

with col_jd:
    st.markdown('<div class="section-title">📋 Job Description</div>', unsafe_allow_html=True)
    jd = st.text_area("", placeholder="Paste the job description here...", height=130, label_visibility="collapsed")

st.markdown("<hr>", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔍  Resume Analysis", "📊  JD Comparison", "🎯  Interview Prep"])


# ── TAB 1 — Resume Analysis ───────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Analyze your resume for instant AI feedback</div>', unsafe_allow_html=True)
    if st.button("✦ Analyze Resume", key="btn_analyze"):
        if not resume:
            st.warning("⚠️ Please upload your resume first.")
        else:
            with st.spinner("Analyzing your resume with AI..."):
                try:
                    text = extract_resume_text(resume)
                    prompt = f"""
You are an expert resume reviewer. Analyze the following resume and return ONLY a valid JSON object with no extra text or markdown.

Resume:
\"\"\"{text[:3000]}\"\"\"

Return this exact JSON structure with real analysis:
{{
  "overall_score": "82/100",
  "ats_score": "75%",
  "sections_count": 5,
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "feedback": "Detailed feedback here."
}}
Return ONLY the JSON, nothing else.
"""
                    result = ask_groq(prompt)

                    st.markdown("### Resume Feedback")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Overall Score", result.get("overall_score", "—"))
                    m2.metric("ATS Compatibility", result.get("ats_score", "—"))
                    m3.metric("Sections Found", result.get("sections_count", "—"))

                    st.markdown("<br>", unsafe_allow_html=True)
                    fcol1, fcol2 = st.columns(2)

                    with fcol1:
                        st.markdown('<div class="section-title">💪 Strengths</div>', unsafe_allow_html=True)
                        for s in result.get("strengths", []):
                            st.markdown(f'<div class="card card-accent">✓ {s}</div>', unsafe_allow_html=True)

                    with fcol2:
                        st.markdown('<div class="section-title">🔧 Improvements</div>', unsafe_allow_html=True)
                        for imp in result.get("improvements", []):
                            st.markdown(f'<div class="card">→ {imp}</div>', unsafe_allow_html=True)

                    if result.get("feedback"):
                        st.markdown('<div class="section-title" style="margin-top:1rem">📝 Detailed Feedback</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card">{result["feedback"]}</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ AI analysis failed: {e}")


# ── TAB 2 — JD Comparison ────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Compare your resume against a job description</div>', unsafe_allow_html=True)
    if st.button("✦ Compare with JD", key="btn_compare"):
        if not resume or not jd:
            st.warning("⚠️ Please upload your resume and paste a job description.")
        else:
            with st.spinner("Comparing resume with job description..."):
                try:
                    resume.seek(0)
                    text = extract_resume_text(resume)
                    prompt = f"""
You are an expert recruiter. Compare the resume against the job description and return ONLY a valid JSON object.

Resume:
\"\"\"{text[:2000]}\"\"\"

Job Description:
\"\"\"{jd[:2000]}\"\"\"

Return this exact JSON:
{{
  "match_score_percentage": 72,
  "present_skills": ["skill1", "skill2"],
  "missing_technical_skills": ["skill1", "skill2"],
  "missing_soft_skills": ["skill1", "skill2"],
  "summary": "Summary here."
}}
Return ONLY the JSON, nothing else.
"""
                    result = ask_groq(prompt)
                    score = float(result.get("match_score_percentage", 0))
                    missing_tech = result.get("missing_technical_skills", [])
                    missing_soft = result.get("missing_soft_skills", [])
                    present = result.get("present_skills", [])

                    ch1, ch2 = st.columns([1, 1.5], gap="large")
                    with ch1:
                        st.markdown('<div class="section-title">Match Score</div>', unsafe_allow_html=True)
                        st.plotly_chart(make_donut_chart(score), use_container_width=True, config={"displayModeBar": False})
                        label = "🟢 Strong Match" if score >= 70 else "🟡 Partial Match" if score >= 40 else "🔴 Low Match"
                        st.markdown(f"<div style='text-align:center; color:#94a3b8'>{label}</div>", unsafe_allow_html=True)

                    with ch2:
                        st.markdown('<div class="section-title">Skills Breakdown</div>', unsafe_allow_html=True)
                        st.plotly_chart(make_skills_bar(present, missing_tech, missing_soft), use_container_width=True, config={"displayModeBar": False})

                    st.markdown("<hr>", unsafe_allow_html=True)
                    sc1, sc2, sc3 = st.columns(3)

                    with sc1:
                        st.markdown('<div class="section-title">✅ Present Skills</div>', unsafe_allow_html=True)
                        if present:
                            st.markdown("".join(f'<span class="skill-tag skill-present">{s}</span>' for s in present), unsafe_allow_html=True)
                        else:
                            st.caption("None detected")

                    with sc2:
                        st.markdown('<div class="section-title">🔴 Missing Technical</div>', unsafe_allow_html=True)
                        if missing_tech:
                            st.markdown("".join(f'<span class="skill-tag skill-missing-tech">{s}</span>' for s in missing_tech), unsafe_allow_html=True)
                        else:
                            st.success("No missing technical skills!")

                    with sc3:
                        st.markdown('<div class="section-title">🟡 Missing Soft Skills</div>', unsafe_allow_html=True)
                        if missing_soft:
                            st.markdown("".join(f'<span class="skill-tag skill-missing-soft">{s}</span>' for s in missing_soft), unsafe_allow_html=True)
                        else:
                            st.success("No missing soft skills!")

                except Exception as e:
                    st.error(f"❌ AI analysis failed: {e}")


# ── TAB 3 — Interview Prep ────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">AI-generated interview questions tailored to your profile</div>', unsafe_allow_html=True)
    if st.button("✦ Generate Interview Questions", key="btn_questions"):
        if not resume or not jd:
            st.warning("⚠️ Please upload your resume and paste a job description.")
        else:
            with st.spinner("Crafting personalised interview questions..."):
                try:
                    resume.seek(0)
                    text = extract_resume_text(resume)
                    prompt = f"""
You are an expert interview coach. Generate tailored interview questions. Return ONLY a valid JSON object.

Resume:
\"\"\"{text[:2000]}\"\"\"

Job Description:
\"\"\"{jd[:2000]}\"\"\"

Return this exact JSON:
{{
  "questions": [
    {{"category": "Technical Skills", "question": "Question here?"}},
    {{"category": "Behavioural", "question": "Question here?"}},
    {{"category": "Role Specific", "question": "Question here?"}},
    {{"category": "Culture Fit", "question": "Question here?"}}
  ]
}}
Generate exactly 10 questions. Return ONLY the JSON, nothing else.
"""
                    result = ask_groq(prompt)
                    questions = result.get("questions", [])

                    if questions:
                        categories = {}
                        for q in questions:
                            cat = q.get("category", "General")
                            text_q = q.get("question", q)
                            categories.setdefault(cat, []).append(text_q)

                        for cat, qs in categories.items():
                            st.markdown(f'<div class="section-title">🎯 {cat}</div>', unsafe_allow_html=True)
                            for i, q in enumerate(qs, 1):
                                st.markdown(f"""
                                <div class="q-card">
                                    <div class="q-number">{i}</div>
                                    {q}
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                    else:
                        st.info("No questions returned.")

                except Exception as e:
                    st.error(f"❌ AI analysis failed: {e}")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; color:#334155; font-size:0.78rem; margin-top:4rem; font-family: DM Sans, sans-serif;'>
    Built with ♥ using Streamlit · AI Resume Assistant
</div>
""", unsafe_allow_html=True)
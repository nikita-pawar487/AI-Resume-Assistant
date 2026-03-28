import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import time

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6f0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero Banner ── */
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
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%);
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

/* ── Tab Styling ── */
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
.stTabs [data-baseweb="tab"]:hover { color: #e2e8f0; background: rgba(255,255,255,0.05); }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #059669) !important;
    color: white !important;
    font-weight: 600;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ── Upload Zone ── */
[data-testid="stFileUploader"] {
    background: rgba(139,92,246,0.06);
    border: 2px dashed rgba(139,92,246,0.3);
    border-radius: 16px;
    padding: 1rem;
    transition: all 0.3s;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(139,92,246,0.6);
    background: rgba(139,92,246,0.1);
}

/* ── Text Area ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    resize: vertical;
}
.stTextArea textarea:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
}

/* ── Buttons ── */
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
    letter-spacing: 0.3px;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124,58,237,0.4);
    filter: brightness(1.1);
}
.stButton > button:active { transform: translateY(0); }

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-accent {
    border-left: 3px solid #7c3aed;
}

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.8rem !important; }
[data-testid="stMetricValue"] { color: #a78bfa !important; font-family: 'Syne', sans-serif !important; }

/* ── Skill Tags ── */
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

/* ── Section Headers ── */
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

/* ── Question Cards ── */
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

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.5rem 0; }

/* ── Success / Error / Warning boxes ── */
.stSuccess { background: rgba(16,185,129,0.08) !important; border: 1px solid rgba(16,185,129,0.2) !important; border-radius: 12px !important; }
.stError   { background: rgba(239,68,68,0.08) !important; border: 1px solid rgba(239,68,68,0.2) !important; border-radius: 12px !important; }
.stWarning { background: rgba(251,191,36,0.08) !important; border: 1px solid rgba(251,191,36,0.2) !important; border-radius: 12px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2d2d3d; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


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
    fig.add_annotation(
        text=f"<b>{score:.0f}%</b>",
        x=0.5, y=0.55, showarrow=False,
        font=dict(size=32, color=color, family="Syne"),
    )
    fig.add_annotation(
        text="Match",
        x=0.5, y=0.38, showarrow=False,
        font=dict(size=13, color="#94a3b8", family="DM Sans"),
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
    )
    return fig


# ── Helper: Skills Bar Chart ─────────────────────────────────────────────────
def make_skills_bar(present: list, missing_tech: list, missing_soft: list) -> go.Figure:
    categories = ["Present", "Missing Technical", "Missing Soft"]
    counts = [len(present), len(missing_tech), len(missing_soft)]
    colors = ["#10b981", "#ef4444", "#f59e0b"]

    fig = go.Figure(go.Bar(
        x=categories, y=counts,
        marker_color=colors,
        text=counts, textposition="outside",
        textfont=dict(color="#e2e8f0", family="DM Sans"),
        width=0.4,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=10, l=10, r=10),
        height=220,
        yaxis=dict(showgrid=False, visible=False),
        xaxis=dict(tickfont=dict(color="#94a3b8", family="DM Sans")),
        font=dict(color="#e2e8f0"),
    )
    return fig


# ── Hero Section ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ AI Powered</div>
    <h1>Resume Assistant</h1>
    <p>Upload your resume, paste a job description, and let AI guide you to your dream role — with smart analysis, skill gap detection & interview prep.</p>
</div>
""", unsafe_allow_html=True)


# ── Shared Upload & JD ───────────────────────────────────────────────────────
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


# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔍  Resume Analysis",
    "📊  JD Comparison",
    "🎯  Interview Prep",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Resume Analysis
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Analyze your resume for instant AI feedback</div>', unsafe_allow_html=True)

    if st.button("✦ Analyze Resume", key="btn_analyze"):
        if not resume:
            st.warning("⚠️ Please upload your resume first.")
        else:
            with st.spinner("Analyzing your resume with AI..."):
                try:
                    files = {"file": resume}
                    res = requests.post("http://127.0.0.1:8000/upload-resume/", files=files)
                    result = res.json()

                    st.markdown("### Resume Feedback")

                    # Key metrics row
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Overall Score", result.get("overall_score", "—"))
                    m2.metric("ATS Compatibility", result.get("ats_score", "—"))
                    m3.metric("Sections Found", result.get("sections_count", "—"))

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Feedback sections
                    feedback = result.get("feedback", "")
                    strengths = result.get("strengths", [])
                    improvements = result.get("improvements", [])

                    fcol1, fcol2 = st.columns(2)
                    with fcol1:
                        st.markdown('<div class="section-title">💪 Strengths</div>', unsafe_allow_html=True)
                        for s in strengths:
                            st.markdown(f'<div class="card card-accent">✓ {s}</div>', unsafe_allow_html=True)

                    with fcol2:
                        st.markdown('<div class="section-title">🔧 Improvements</div>', unsafe_allow_html=True)
                        for imp in improvements:
                            st.markdown(f'<div class="card">→ {imp}</div>', unsafe_allow_html=True)

                    if feedback:
                        st.markdown('<div class="section-title" style="margin-top:1rem">📝 Detailed Feedback</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card">{feedback}</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Could not reach the backend: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — JD Comparison
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Compare your resume against a job description</div>', unsafe_allow_html=True)

    if st.button("✦ Compare with JD", key="btn_compare"):
        if not resume or not jd:
            st.warning("⚠️ Please upload your resume and paste a job description.")
        else:
            with st.spinner("Comparing resume with job description..."):
                try:
                    files = {"file": resume}
                    data  = {"job_description": jd}
                    res   = requests.post("http://127.0.0.1:8000/compare-with-jd/", files=files, data=data)
                    result = res.json()

                    score         = float(result.get("match_score_percentage", 0))
                    missing_tech  = result.get("missing_technical_skills", [])
                    missing_soft  = result.get("missing_soft_skills", [])
                    present       = result.get("present_skills", [])

                    # ── Score + Bar chart ──
                    ch1, ch2 = st.columns([1, 1.5], gap="large")

                    with ch1:
                        st.markdown('<div class="section-title">Match Score</div>', unsafe_allow_html=True)
                        st.plotly_chart(make_donut_chart(score), use_container_width=True, config={"displayModeBar": False})

                        label = "🟢 Strong Match" if score >= 70 else "🟡 Partial Match" if score >= 40 else "🔴 Low Match"
                        st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.9rem'>{label}</div>", unsafe_allow_html=True)

                    with ch2:
                        st.markdown('<div class="section-title">Skills Breakdown</div>', unsafe_allow_html=True)
                        st.plotly_chart(make_skills_bar(present, missing_tech, missing_soft), use_container_width=True, config={"displayModeBar": False})

                    st.markdown("<hr>", unsafe_allow_html=True)

                    # ── Skills Tags ──
                    sc1, sc2, sc3 = st.columns(3)

                    with sc1:
                        st.markdown('<div class="section-title">✅ Present Skills</div>', unsafe_allow_html=True)
                        if present:
                            tags = "".join(f'<span class="skill-tag skill-present">{s}</span>' for s in present)
                            st.markdown(tags, unsafe_allow_html=True)
                        else:
                            st.caption("None detected")

                    with sc2:
                        st.markdown('<div class="section-title">🔴 Missing Technical</div>', unsafe_allow_html=True)
                        if missing_tech:
                            tags = "".join(f'<span class="skill-tag skill-missing-tech">{s}</span>' for s in missing_tech)
                            st.markdown(tags, unsafe_allow_html=True)
                        else:
                            st.success("No missing technical skills!")

                    with sc3:
                        st.markdown('<div class="section-title">🟡 Missing Soft Skills</div>', unsafe_allow_html=True)
                        if missing_soft:
                            tags = "".join(f'<span class="skill-tag skill-missing-soft">{s}</span>' for s in missing_soft)
                            st.markdown(tags, unsafe_allow_html=True)
                        else:
                            st.success("No missing soft skills!")

                except Exception as e:
                    st.error(f"❌ Could not reach the backend: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Interview Prep
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">AI-generated interview questions tailored to your profile</div>', unsafe_allow_html=True)

    if st.button("✦ Generate Interview Questions", key="btn_questions"):
        if not resume or not jd:
            st.warning("⚠️ Please upload your resume and paste a job description.")
        else:
            with st.spinner("Crafting personalised interview questions..."):
                try:
                    files = {"file": resume}
                    data  = {"job_description": jd}
                    res   = requests.post("http://127.0.0.1:8000/generate-questions/", files=files, data=data)
                    result = res.json()

                    questions = result.get("questions", [])

                    if questions:
                        categories = {}
                        for q in questions:
                            cat = q.get("category", "General") if isinstance(q, dict) else "General"
                            text = q.get("question", q) if isinstance(q, dict) else q
                            categories.setdefault(cat, []).append(text)

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
                        st.info("No questions returned. Check your backend response format.")

                except Exception as e:
                    st.error(f"❌ Could not reach the backend: {e}")


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; color:#334155; font-size:0.78rem; margin-top:4rem; font-family: DM Sans, sans-serif;'>
    Built with ♥ using Streamlit · AI Resume Assistant
</div>
""", unsafe_allow_html=True)
@echo off
start cmd /k "cd C:\Users\nikit\OneDrive\Desktop\AI-Resume-Assistant && venv\Scripts\activate && set GROQ_API_KEY=your_groq_key_here && uvicorn main:app --reload"
timeout /t 3
start cmd /k "cd C:\Users\nikit\OneDrive\Desktop\AI-Resume-Assistant && venv\Scripts\activate && streamlit run app.py"
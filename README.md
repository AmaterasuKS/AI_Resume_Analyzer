# 🧾 AI Resume Analyzer

<p align="center">
  <strong>Upload your resume. Paste the job description. Get an AI-powered match analysis in seconds.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/AmaterasuKS/AI_Resume_Analyzer?style=for-the-badge&logo=github&color=6366f1&labelColor=1e1b4b" alt="Stars" />
  <img src="https://img.shields.io/github/forks/AmaterasuKS/AI_Resume_Analyzer?style=for-the-badge&logo=github&color=8b5cf6&labelColor=1e1b4b" alt="Forks" />
  <img src="https://img.shields.io/github/license/AmaterasuKS/AI_Resume_Analyzer?style=for-the-badge&color=06b6d4&labelColor=0f172a" alt="License" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Groq-API-000000?style=flat-square" alt="Groq API" />
  <img src="https://img.shields.io/badge/LLM-llama--3.3--70b-8b5cf6?style=flat-square" alt="Llama 3.3 70B" />
  <img src="https://img.shields.io/badge/UI-Tailwind%20CSS-38bdf8?style=flat-square&logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
</p>

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 📄 **Multi-format** | Upload PDF, DOCX or TXT resumes |
| 🎯 **Match score** | 0–100% fit with the job description |
| 💪 **Strengths & weaknesses** | Clear breakdown of what works and what doesn’t |
| 💡 **Suggestions** | Concrete tips to improve your resume |
| 🤖 **Ask AI** | Ask follow-up questions about your fit for the role |
| 🌐 **EN / RU** | Full interface and AI output in English or Russian |
| 🔄 **Live translation** | Switch language and the analysis text translates on the fly |
| 🎨 **Modern UI** | Gradient theme, compact layout, hover effects |

---

## 🖼 Screenshot

<img width="1905" height="969" alt="image" src="https://github.com/user-attachments/assets/fcdc1063-dfc6-4b0c-9041-6f8064562fac" />
<img width="1910" height="967" alt="image" src="https://github.com/user-attachments/assets/55c319a9-48d4-4044-80ad-a4d95f4245cf" />



---

## 🛠 Tech stack

- **Backend:** Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **AI:** [Groq API](https://console.groq.com/) — model `llama-3.3-70b-versatile`
- **Resume parsing:** [PyMuPDF](https://pymupdf.readthedocs.io/) (PDF), [python-docx](https://python-docx.readthedocs.io/) (Word)
- **Frontend:** Single-page HTML + [Tailwind CSS](https://tailwindcss.com/) (CDN), vanilla JS

---

## 📦 Installation

### 1. Clone and enter the project

```bash
git clone https://github.com/AmaterasuKS/AI_Resume_Analyzer.git
cd AI_Resume_Analyzer/resume-analyzer
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
# Windows
copy .env.example .env
# Linux / macOS
# cp .env.example .env
```

Edit `.env` and set your Groq API key:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
```

Get a free key at **[console.groq.com](https://console.groq.com/)**.

### 4. Run the app

```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

---

## 🚀 Usage

1. **Choose language** — EN or RU (top right).
2. **Upload resume** — drag & drop or click (PDF, DOCX or TXT).
3. **Paste job description** — full text of the vacancy.
4. **Click *Analyze*** — wait for the match score, summary, strengths, weaknesses and suggestions.
5. **Ask questions** — use the chat at the bottom to ask the AI anything about your fit for the role (e.g. what to highlight in the interview).
6. **Switch language** — change EN/RU anytime; the analysis text is translated automatically.

---

## 🔌 API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the web UI |
| `POST` | `/analyze` | Form: `file`, `job_description`, `lang` → analysis JSON |
| `POST` | `/question` | JSON: `question`, `resume_text`, `job_description`, `lang` → answer |
| `POST` | `/translate_analysis` | JSON: analysis fields + `target_lang` → translated analysis |

Interactive docs: **http://127.0.0.1:8000/docs** (Swagger UI).

---

## ⚙️ How it works

The app extracts text from your resume (PDF via PyMuPDF, DOCX via python-docx), then sends it together with the job description to Groq’s LLM. The model returns a structured analysis (match score, strengths, weaknesses, suggestions, summary) in the chosen language. The same model answers your follow-up questions. When you switch the UI language, the displayed analysis is re-translated via `/translate_analysis` so everything stays consistent.

---

## 📁 Project structure

```
resume-analyzer/
├── main.py              # FastAPI app & routes
├── core/
│   ├── __init__.py
│   ├── models.py        # Pydantic models
│   ├── file_reader.py   # PDF / DOCX / TXT parsing
│   └── ai_analyzer.py   # Groq calls (analyze, question, translate)
├── static/
│   └── index.html       # Single-page UI
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📄 License

[MIT](LICENSE) — use it as you like.

---

<p align="center">
  <sub>Made with FastAPI + Groq + Tailwind</sub>
</p>

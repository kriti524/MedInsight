# 🩺 MedInsight — Health Prediction Application

A full-featured patient health management app built with **Python + Streamlit**, featuring AI-powered blood test analysis via the **Claude AI API**.

---

## Features

- ✅ **CRUD Operations** — Create, Read, Update, Delete patient records
- 🤖 **AI Health Remarks** — Automatic risk prediction using Claude AI (with rule-based fallback)
- 🧪 **Blood Test Analysis** — Glucose, Haemoglobin, Cholesterol assessment
- 🛡️ **Data Validation** — Email format, future DOB guard, numeric range checks
- 💾 **Persistent Storage** — SQLite database (auto-created on first run)
- 🎨 **Clean UI** — Dark-themed, responsive Streamlit interface

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Set your Anthropic API key

The app calls the Claude API for health predictions. If no API key is available, it falls back to a built-in rule-based predictor.

```bash
# Linux / macOS
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Or create a `.streamlit/secrets.toml` file:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

### 3. Run the application

```bash
cd health_app
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## Project Structure

```
health_app/
├── app.py              # Main Streamlit UI (all pages)
├── database.py         # SQLite CRUD layer
├── ai_prediction.py    # Claude API + fallback predictor
├── validators.py       # Input validation helpers
├── requirements.txt    # Python dependencies
├── patients.db         # SQLite DB (auto-created)
└── README.md
```

---

## Blood Test Reference Ranges

| Marker       | Normal                        | Borderline          | High Risk      |
|--------------|-------------------------------|---------------------|----------------|
| Glucose      | 70–100 mg/dL                  | 100–125 mg/dL       | >125 mg/dL     |
| Haemoglobin  | Men 13.5–17.5 / Women 12–15.5 | Slightly below      | <12 g/dL       |
| Cholesterol  | <200 mg/dL                    | 200–239 mg/dL       | ≥240 mg/dL     |

---

## AI Integration

The app sends patient blood values to the **Claude claude-sonnet-4-20250514** model via the Anthropic `/v1/messages` API. If the API is unavailable or unauthenticated, the built-in rule-based fallback system provides predictions locally without any external call.

---

## Notes

- This app is for **educational/demonstration purposes only**
- Not a substitute for professional medical advice
- Patient data is stored locally in `patients.db` (SQLite)

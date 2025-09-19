# Blindspot AI Security Sandbox

Blindspot is an AI assurance sandbox for LLM prompts. Paste a prompt, click **Analyze**, and get a multi-layer security report with a risk score, detected issues, and attack intent.

![Dashboard](Blindspot/docs/screenshots/textbox.png)
![Insight Report](Blindspot/docs/screenshots/details.png)
![Recent Scans](Blindspot/docs/screenshots/scans.png)

## Features
- Interactive sandbox UI with Overall Risk Score, Prompt Metadata, Detailed Findings, and Recent Scans
- Multi-layer detection: PII patterns, semantic risk, language ID, and intent classification
- Zero-shot intent classification with BART MNLI, plus regex fallbacks for high-signal cues
- Fast after first run. The first run downloads models from Hugging Face

## How it works
- **PII Detector**: regex for emails, phones, cards, and passwords  
- **Language Detector**: transformers language ID used for contextual risk  
- **Semantic Risk**: sentence-transformers (`all-MiniLM-L6-v2`) compared to `threat_intelligence.json` yields a score from 0.0 to 1.0  
- **Attack Classifier**: zero-shot over security labels (Jailbreak, Prompt Injection, Data Exfiltration, Misinformation, Harmful, Hate, PII Harvesting) plus regex cues  
- **Scanner Service**: merges findings, bumps moderate non-English risk, and returns the final report

## Stack
Python 3.10+, FastAPI, Uvicorn  
Vanilla JS, HTML, CSS, Chart.js  
transformers, sentence-transformers, torch

## Quick start

```bash
# 1) Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS or Linux
source venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Start the backend API
cd Blindspot
uvicorn backend.main:app --reload
# API runs at http://127.0.0.1:8000

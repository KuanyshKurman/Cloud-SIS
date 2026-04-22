# 🏗️ Almaty Tender Analyzer v1.0

**AI-powered construction tender risk analysis for Kazakhstan SMEs**

---

## Business Value

Construction SMEs in Almaty spend up to **3 working days** manually reviewing a single tender lot (100+ page PDFs). Critical risks, licensing requirements, and penalties are buried in unstructured legal text.

**Almaty Tender Analyzer** reduces that to **under 30 seconds**, delivering:

- Detection of hidden penalties and contract asymmetries
- Automatic identification of GSL (State Licensing) categories (Level 1 / 2 / 3)
- Project deadline normalization into working days
- Material and compliance requirement extraction
- Color-coded overall risk score (0–100)

---

## Setup Instructions

### 1. Clone or download this project

```bash
git clone <repo-url>
cd almaty-tender-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your Gemini API key

Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) and create a free API key.

### 4. Launch the application

```bash
streamlit run app.py
```

### 5. Usage

1. Enter your Gemini API key in the sidebar
2. Upload a **text-based PDF** tender document
3. Click **🚀 Analyze Tender**
4. Review the structured risk dashboard

> **Note:** Scanned (image-based) PDFs are not supported. Use a text PDF or an OCR-processed version.

---

## Architecture

```
app.py          → UI layer (Streamlit) — zero business logic
processor.py    → AI pipeline: PDF extraction → Gemini → JSON
requirements.txt → Dependencies
```

---

## Legal Disclaimer

This tool is a **decision-support system only**. The AI-generated analysis is intended to assist tender department staff in initial document review. **Final legal and financial decisions must be validated by qualified legal and procurement professionals.**

Token usage can be monitored via [Google AI Studio Dashboard](https://aistudio.google.com/).
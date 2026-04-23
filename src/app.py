import streamlit as st
from processor import process_tender_pdf

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Almaty Tender Analyzer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# DARK THEME STYLE
# =========================
st.markdown(
    """
    <style>
        body { background-color: #0e1117; }
        .main { background-color: #0e1117; }

        .card {
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            background-color: #161b22;
            border: 1px solid #2a2f3a;
        }
        .risk-high {
            background-color: #3a0f0f;
            border-left: 5px solid #ff4b4b;
        }
        .risk-medium {
            background-color: #3a2f0f;
            border-left: 5px solid #f0a500;
        }
        .risk-low {
            background-color: #0f3a1a;
            border-left: 5px solid #2ecc71;
        }
        .kpi-box {
            padding: 24px;
            border-radius: 14px;
            background-color: #161b22;
            border: 1px solid #2a2f3a;
            text-align: center;
            margin-bottom: 20px;
        }
        .kpi-score {
            font-size: 64px;
            font-weight: 800;
            line-height: 1;
        }
        .kpi-label {
            color: #8b949e;
            font-size: 14px;
            margin-top: 6px;
        }
        .title { font-size: 28px; font-weight: 700; color: #ffffff; }
        .subtitle { color: #8b949e; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ System Config")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="sk-proj-...")
st.sidebar.markdown("---")
st.sidebar.info("Almaty Tender Analyzer v1.0\n\nAI-powered construction tender intelligence.")
st.sidebar.markdown("---")
st.sidebar.caption(
    "⚠️ Disclaimer: This tool is a decision-support system only. "
    "Final legal decisions must be validated by qualified professionals."
)

# =========================
# MAIN HEADER
# =========================
st.markdown("<div class='title'>🏗️ Almaty Tender Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered construction tender risk analysis for Kazakhstan SMEs</div>", unsafe_allow_html=True)
st.write("---")

# =========================
# FILE UPLOAD
# =========================
uploaded_file = st.file_uploader("Upload Tender PDF", type=["pdf"])

if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar to proceed.")

# =========================
# PROCESS BUTTON
# =========================
if uploaded_file and api_key:
    if st.button("🚀 Analyze Tender", type="primary"):
        with st.spinner("Analyzing tender document with Gemini AI..."):
            result = process_tender_pdf(uploaded_file, api_key)

        # ERROR HANDLING
        if "error" in result:
            st.error(f"❌ {result['error']}")
            if "raw_output" in result:
                with st.expander("Raw output (debug)"):
                    st.code(result["raw_output"])
            st.stop()

        st.success("✅ Analysis complete")

        # =========================
        # KPI — RISK SCORE
        # =========================
        risk_score = result.get("Общий уровень риска", None)
        if risk_score is not None:
            try:
                score = int(risk_score)
            except (ValueError, TypeError):
                score = None

            if score is not None:
                if score >= 70:
                    color = "#ff4b4b"
                    label = "HIGH RISK"
                elif score >= 40:
                    color = "#f0a500"
                    label = "MEDIUM RISK"
                else:
                    color = "#2ecc71"
                    label = "LOW RISK"

                st.markdown(
                    f"""
                    <div class="kpi-box">
                        <div class="kpi-score" style="color:{color}">{score}/100</div>
                        <div class="kpi-label">Overall Risk Score — <b>{label}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # SUMMARY
        summary = result.get("Резюме")
        if summary:
            st.info(f"📋 **Summary:** {summary}")

        # =========================
        # DASHBOARD
        # =========================
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("## ⚠️ Risks")
            risks = result.get("Наличие скрытых штрафов", "Not specified")
            risk_class = "risk-high" if risks and risks != "Не указано" else "card"
            st.markdown(
                f'<div class="card {risk_class}"><h4>Hidden Penalties / Risks</h4><p>{risks}</p></div>',
                unsafe_allow_html=True
            )

        with col2:
            st.markdown("## ⏳ Timeline")
            deadline = result.get("Сроки выполнения работ", "Not specified")
            st.markdown(
                f'<div class="card"><h4>Project Deadline</h4><p>{deadline}</p></div>',
                unsafe_allow_html=True
            )

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("## 📜 Licenses (GSL)")
            licenses = result.get("Требуемые категории ГСЛ", "Not specified")
            st.markdown(
                f'<div class="card risk-low"><h4>Required Licenses</h4><p>{licenses}</p></div>',
                unsafe_allow_html=True
            )

        with col4:
            st.markdown("## 🧱 Materials")
            materials = result.get("Особые требования к материалам", "Not specified")
            st.markdown(
                f'<div class="card"><h4>Material Requirements</h4><p>{materials}</p></div>',
                unsafe_allow_html=True
            )

        # =========================
        # RAW JSON (DEBUG)
        # =========================
        with st.expander("🔍 Raw AI Output (JSON)"):
            st.json(result)

else:
    st.info("📂 Please upload a PDF file and enter your Gemini API key to start analysis.")
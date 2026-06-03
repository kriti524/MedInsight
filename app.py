import streamlit as st
import pandas as pd
from datetime import date, datetime

import database as db
import validators as val
import ai_prediction as ai

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedInsight · Health Predictor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border-right: 1px solid #334155;
}

[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 0.9rem;
}

/* Header */
.hero-header {
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 600;
    margin-bottom: 0.2rem;
}

.hero-sub {
    color: #64748b;
    font-size: 0.95rem;
    margin-bottom: 2rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Cards */
.metric-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

/* Status badges */
.badge-normal { background:#064e3b; color:#6ee7b7; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-risk   { background:#7f1d1d; color:#fca5a5; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-warn   { background:#78350f; color:#fcd34d; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(14,165,233,0.35) !important;
}

/* Delete button override */
.del-btn > button {
    background: linear-gradient(135deg, #dc2626, #991b1b) !important;
}

/* Form inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stSelectbox > div > div {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

/* Table */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Divider */
hr { border-color: #334155 !important; }

/* Success / Error messages */
.stSuccess { background: #064e3b !important; border: 1px solid #6ee7b7 !important; }
.stError   { background: #7f1d1d !important; border: 1px solid #fca5a5 !important; }
.stWarning { background: #78350f !important; border: 1px solid #fcd34d !important; }

/* Spinner text */
.stSpinner p { color: #94a3b8 !important; }

/* Section titles */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: #e2e8f0;
    margin-bottom: 1rem;
    border-left: 3px solid #0ea5e9;
    padding-left: 0.75rem;
}

/* Remarks box */
.remarks-box {
    background: #1e293b;
    border: 1px solid #0ea5e9;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    color: #94a3b8;
    font-size: 0.92rem;
    line-height: 1.6;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Init DB ────────────────────────────────────────────────────────────────────
db.init_db()


# ─── Helpers ───────────────────────────────────────────────────────────────────
def risk_badge(glucose, haemoglobin, cholesterol):
    issues = 0
    if glucose > 125 or cholesterol >= 240 or haemoglobin < 12:
        issues += 1
    if glucose > 200 or cholesterol >= 300:
        issues += 1
    if issues == 0:
        return '<span class="badge-normal">✓ Normal</span>'
    elif issues == 1:
        return '<span class="badge-warn">⚠ Borderline</span>'
    else:
        return '<span class="badge-risk">✗ High Risk</span>'


def format_dob(dob_str):
    try:
        d = datetime.strptime(dob_str, "%Y-%m-%d")
        return d.strftime("%d %b %Y")
    except Exception:
        return dob_str


# ─── Sidebar Nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🩺 MedInsight")
    st.markdown("*AI-Powered Health Predictor*")
    st.divider()
    page = st.radio(
        "Navigation",
        ["📋 Patient Records", "➕ Add Patient", "✏️ Edit Patient", "🗑️ Delete Patient"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown("<small style='color:#475569'>Powered by Claude AI<br>SQLite Persistent Storage</small>", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-header">MedInsight Health Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Blood Test Analysis · AI-Powered Risk Assessment · Patient Management</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: Patient Records (READ)
# ════════════════════════════════════════════════════════════════════════════════
if page == "📋 Patient Records":
    st.markdown('<div class="section-title">All Patient Records</div>', unsafe_allow_html=True)

    patients = db.get_all_patients()

    if not patients:
        st.info("No patient records yet. Use **➕ Add Patient** to create the first record.")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Patients", len(patients))
        high_risk = sum(1 for p in patients if p["glucose"] > 125 or p["cholesterol"] >= 240 or p["haemoglobin"] < 12)
        col2.metric("High/Borderline Risk", high_risk)
        avg_glucose = round(sum(p["glucose"] for p in patients) / len(patients), 1)
        col3.metric("Avg Glucose (mg/dL)", avg_glucose)
        avg_chol = round(sum(p["cholesterol"] for p in patients) / len(patients), 1)
        col4.metric("Avg Cholesterol (mg/dL)", avg_chol)

        st.divider()

        # Search/Filter
        search = st.text_input("🔍 Search by name or email", placeholder="Type to filter...")

        filtered = patients
        if search:
            q = search.lower()
            filtered = [p for p in patients if q in p["full_name"].lower() or q in p["email"].lower()]

        st.markdown(f"*Showing {len(filtered)} of {len(patients)} records*")
        st.divider()

        for p in filtered:
            with st.container():
                col_info, col_bio, col_badge = st.columns([3, 3, 1.5])

                with col_info:
                    st.markdown(f"**{p['full_name']}**  `#{p['id']}`")
                    st.markdown(f"📧 {p['email']}")
                    st.markdown(f"🎂 {format_dob(p['date_of_birth'])}")

                with col_bio:
                    st.markdown(f"🩸 Glucose: **{p['glucose']} mg/dL**")
                    st.markdown(f"🔴 Haemoglobin: **{p['haemoglobin']} g/dL**")
                    st.markdown(f"💛 Cholesterol: **{p['cholesterol']} mg/dL**")

                with col_badge:
                    st.markdown(risk_badge(p["glucose"], p["haemoglobin"], p["cholesterol"]), unsafe_allow_html=True)
                    st.markdown(f"<small style='color:#475569'>Updated:<br>{p['updated_at'][:10]}</small>", unsafe_allow_html=True)

                if p.get("remarks"):
                    with st.expander("🤖 AI Health Remarks"):
                        st.markdown(f'<div class="remarks-box">{p["remarks"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown("*No AI remarks yet — re-save to generate.*")

                st.divider()

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: Add Patient (CREATE)
# ════════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Patient":
    st.markdown('<div class="section-title">Add New Patient</div>', unsafe_allow_html=True)

    with st.form("add_patient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *", placeholder="e.g. Priya Sharma")
            email = st.text_input("Email Address *", placeholder="patient@example.com")
            dob = st.date_input("Date of Birth *",
                                value=date(1990, 1, 1),
                                min_value=date(1900, 1, 1),
                                max_value=date.today())
        with col2:
            glucose = st.number_input("Glucose (mg/dL) *", min_value=0.0, max_value=600.0, value=90.0, step=0.1,
                                      help="Normal fasting: 70–100 mg/dL")
            haemoglobin = st.number_input("Haemoglobin (g/dL) *", min_value=0.0, max_value=25.0, value=13.5, step=0.1,
                                          help="Normal: Men 13.5–17.5, Women 12.0–15.5 g/dL")
            cholesterol = st.number_input("Total Cholesterol (mg/dL) *", min_value=0.0, max_value=700.0, value=180.0, step=0.1,
                                          help="Desirable: <200 mg/dL")

        submitted = st.form_submit_button("💾 Save Patient & Generate AI Remarks", use_container_width=True)

    if submitted:
        errors = val.validate_patient_form(full_name, dob, email, glucose, haemoglobin, cholesterol)
        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            with st.spinner("🤖 Calling AI for health prediction…"):
                remarks = ai.get_health_prediction(full_name, str(dob), glucose, haemoglobin, cholesterol)

            patient_id = db.create_patient(
                full_name=full_name.strip(),
                date_of_birth=str(dob),
                email=email.strip().lower(),
                glucose=float(glucose),
                haemoglobin=float(haemoglobin),
                cholesterol=float(cholesterol),
                remarks=remarks
            )

            if patient_id:
                st.success(f"✅ Patient **{full_name}** added successfully! (ID: {patient_id})")
                st.markdown("**🤖 AI Health Remarks:**")
                st.markdown(f'<div class="remarks-box">{remarks}</div>', unsafe_allow_html=True)
            else:
                st.error("❌ A patient with this email already exists.")

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: Edit Patient (UPDATE)
# ════════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Edit Patient":
    st.markdown('<div class="section-title">Edit Patient Record</div>', unsafe_allow_html=True)

    patients = db.get_all_patients()
    if not patients:
        st.info("No patient records found. Add a patient first.")
    else:
        patient_options = {f"#{p['id']} — {p['full_name']} ({p['email']})": p['id'] for p in patients}
        selected_label = st.selectbox("Select patient to edit", list(patient_options.keys()))
        selected_id = patient_options[selected_label]

        p = db.get_patient_by_id(selected_id)

        if p:
            with st.form("edit_patient_form"):
                col1, col2 = st.columns(2)
                with col1:
                    full_name = st.text_input("Full Name *", value=p["full_name"])
                    email = st.text_input("Email Address *", value=p["email"])
                    try:
                        dob_val = datetime.strptime(p["date_of_birth"], "%Y-%m-%d").date()
                    except Exception:
                        dob_val = date(1990, 1, 1)
                    dob = st.date_input("Date of Birth *", value=dob_val,
                                        min_value=date(1900, 1, 1), max_value=date.today())
                with col2:
                    glucose = st.number_input("Glucose (mg/dL) *", min_value=0.0, max_value=600.0,
                                               value=float(p["glucose"]), step=0.1)
                    haemoglobin = st.number_input("Haemoglobin (g/dL) *", min_value=0.0, max_value=25.0,
                                                   value=float(p["haemoglobin"]), step=0.1)
                    cholesterol = st.number_input("Cholesterol (mg/dL) *", min_value=0.0, max_value=700.0,
                                                   value=float(p["cholesterol"]), step=0.1)

                regen = st.checkbox("🔄 Regenerate AI health remarks", value=False)
                submitted = st.form_submit_button("💾 Update Patient Record", use_container_width=True)

            if submitted:
                errors = val.validate_patient_form(full_name, dob, email, glucose, haemoglobin, cholesterol)
                if errors:
                    for e in errors:
                        st.error(f"❌ {e}")
                else:
                    remarks = p.get("remarks", "")
                    if regen or not remarks:
                        with st.spinner("🤖 Regenerating AI health prediction…"):
                            remarks = ai.get_health_prediction(full_name, str(dob), glucose, haemoglobin, cholesterol)

                    success = db.update_patient(
                        patient_id=selected_id,
                        full_name=full_name.strip(),
                        date_of_birth=str(dob),
                        email=email.strip().lower(),
                        glucose=float(glucose),
                        haemoglobin=float(haemoglobin),
                        cholesterol=float(cholesterol),
                        remarks=remarks
                    )
                    if success:
                        st.success(f"✅ Patient **{full_name}** updated successfully!")
                        if regen:
                            st.markdown("**🤖 Updated AI Health Remarks:**")
                            st.markdown(f'<div class="remarks-box">{remarks}</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ Update failed. Email may already be in use by another patient.")

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: Delete Patient (DELETE)
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🗑️ Delete Patient":
    st.markdown('<div class="section-title">Delete Patient Record</div>', unsafe_allow_html=True)

    patients = db.get_all_patients()
    if not patients:
        st.info("No patient records found.")
    else:
        patient_options = {f"#{p['id']} — {p['full_name']} ({p['email']})": p['id'] for p in patients}
        selected_label = st.selectbox("Select patient to delete", list(patient_options.keys()))
        selected_id = patient_options[selected_label]

        p = db.get_patient_by_id(selected_id)
        if p:
            st.markdown("**Patient Details:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"- **Name:** {p['full_name']}")
                st.markdown(f"- **Email:** {p['email']}")
                st.markdown(f"- **DOB:** {format_dob(p['date_of_birth'])}")
            with col2:
                st.markdown(f"- **Glucose:** {p['glucose']} mg/dL")
                st.markdown(f"- **Haemoglobin:** {p['haemoglobin']} g/dL")
                st.markdown(f"- **Cholesterol:** {p['cholesterol']} mg/dL")

            if p.get("remarks"):
                st.markdown(f'<div class="remarks-box"><strong>AI Remarks:</strong> {p["remarks"]}</div>', unsafe_allow_html=True)

            st.warning(f"⚠️ You are about to permanently delete **{p['full_name']}'s** record. This action cannot be undone.")

            confirm = st.checkbox(f"I confirm I want to delete {p['full_name']}'s record")
            if confirm:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("🗑️ Delete Patient Record", use_container_width=True):
                    if db.delete_patient(selected_id):
                        st.success(f"✅ Patient **{p['full_name']}** has been deleted.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete the record.")
                st.markdown('</div>', unsafe_allow_html=True)

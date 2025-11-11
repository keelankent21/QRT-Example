
import os
import io
import json
import streamlit as st
from analysis import run_strategic_analysis
from exporters import to_markdown_report, risks_to_csv_bytes, markdown_to_pdf_bytes

st.set_page_config(page_title="QRT Strategic Analyst", page_icon="⚡", layout="wide")

USERNAME = os.getenv("APP_USERNAME", "")
PASSWORD = os.getenv("APP_PASSWORD", "")

def auth_gate():
    if not USERNAME or not PASSWORD:
        return True
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if st.session_state.auth:
        return True
    with st.form("login"):
        st.markdown("### Sign in")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        ok = st.form_submit_button("Sign in")
        if ok and u == USERNAME and p == PASSWORD:
            st.session_state.auth = True
            return True
    st.stop()

auth_gate()

col_logo, col_title = st.columns([1, 6], vertical_alignment="center")
with col_logo:
    st.image("static/qrt_logo.png", width=80)
with col_title:
    st.title("⚡ QRT Strategic Analyst")
    st.caption("PESTEL · SWOT · Risk · Legal · Fiscal · Logistics Analyzer")

with st.sidebar:
    st.header("Project Inputs")
    country = st.text_input("Country", "Mauritius")
    technology = st.text_input("Technology", "PV + BESS")
    capacity_mw = st.number_input("Capacity (MW)", min_value=0.0, value=10.0, step=0.5)
    client = st.text_input("Client", "QRT Power")
    offtaker = st.text_input("Offtaker / Buyer", "CEB (example)")
    horizon = st.selectbox("Horizon", ["Short-term", "Mid-term", "Long-term"], index=1)
    extra_context = st.text_area("Extra context (optional)", placeholder="Sites, ports, EPC candidates, known constraints, tariffs, etc.")
    uploaded = st.file_uploader("Attach additional context (PDF/TXT/DOCX/CSV)…", accept_multiple_files=True)

    run_btn = st.button("Run Strategic Analysis", type="primary")

if run_btn:
    with st.spinner("Analyzing…"):
        attachments = {}
        for f in uploaded or []:
            try:
                attachments[f.name] = f.read().decode("utf-8", errors="ignore")
            except Exception:
                attachments[f.name] = f.getvalue()
        res = run_strategic_analysis(
            country=country,
            technology=technology,
            capacity_mw=capacity_mw,
            client=client,
            offtaker=offtaker,
            horizon=horizon,
            user_context=extra_context,
            attachments=attachments
        )
        st.session_state.res = res

if "res" not in st.session_state:
    st.info("Enter project details on the left and click **Run Strategic Analysis**.")
else:
    res = st.session_state.res
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("Executive Summary")
        st.write(res["executive_summary"])

        st.subheader("PESTEL")
        st.table(res["pestel"])

        st.subheader("SWOT")
        c3, c4 = st.columns(2)
        with c3:
            st.write("**Strengths**")
            st.write("\n".join([f"- {x}" for x in res["swot"]["strengths"]]))
            st.write("**Opportunities**")
            st.write("\n".join([f"- {x}" for x in res["swot"]["opportunities"]]))
        with c4:
            st.write("**Weaknesses**")
            st.write("\n".join([f"- {x}" for x in res["swot"]["weaknesses"]]))
            st.write("**Threats**")
            st.write("\n".join([f"- {x}" for x in res["swot"]["threats"]]))

        st.subheader("Legal & Fiscal")
        st.write(res["legal_fiscal"])

        st.subheader("Logistics & Infrastructure")
        st.write(res["logistics"])

        st.subheader("Recommendations")
        st.write("\n".join([f"- {x}" for x in res["recommendations"]]))

    with col2:
        st.subheader("Top Risks (auto-prioritized)")
        st.dataframe(res["risks"])
        md = to_markdown_report(res)
        st.download_button("⬇️ Download Report (Markdown)", md.encode("utf-8"), file_name="QRT_Strategic_Analysis.md")

        csv_bytes = risks_to_csv_bytes(res["risks"])
        st.download_button("⬇️ Download Risks (CSV)", csv_bytes, file_name="QRT_Risks.csv", mime="text/csv")

        pdf_bytes = markdown_to_pdf_bytes(md)
        if pdf_bytes:
            st.download_button("⬇️ Download Report (PDF)", pdf_bytes, file_name="QRT_Strategic_Analysis.pdf", mime="application/pdf")
        else:
            st.caption("Tip: PDF export is optional and may require wkhtmltopdf on the host.")

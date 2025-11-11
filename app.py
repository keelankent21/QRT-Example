import os, json, streamlit as st
from analysis import run_strategic_analysis
from exporters import to_markdown_report, risks_to_csv_bytes, markdown_to_pdf_bytes
from finance import quick_scenarios, sensitivity_tariff
from visuals import risk_heatmap, pestel_radar
from storage import save_analysis, list_analyses, load_analysis
from advisor import ask_advisor

st.set_page_config(page_title="QRT Strategic Analyst", page_icon="⚡", layout="wide")

# --- Auth opcional ---
USERNAME = os.getenv("APP_USERNAME", "")
PASSWORD = os.getenv("APP_PASSWORD", "")
def auth_gate():
    if not USERNAME or not PASSWORD: return True
    if "auth" not in st.session_state: st.session_state.auth = False
    if st.session_state.auth: return True
    with st.form("login"):
        st.markdown("### Sign in")
        u = st.text_input("Username"); p = st.text_input("Password", type="password")
        if st.form_submit_button("Sign in") and u == USERNAME and p == PASSWORD:
            st.session_state.auth = True; return True
    st.stop()
auth_gate()

# --- Header ---
col_logo, col_title = st.columns([1, 6], vertical_alignment="center")
with col_logo:
    try: st.image("static/qrt_logo.png", width=80)
    except Exception: st.write("")
with col_title:
    st.title("⚡ QRT Strategic Analyst")
    st.caption("PESTEL · SWOT · Risk · Legal · Fiscal · Logistics Analyzer · Finance · Advisor")

# --- Sidebar inputs ---
with st.sidebar:
    st.header("Project Inputs")
    country = st.text_input("Country", "Mauritius")
    technology = st.text_input("Technology", "PV + BESS")
    capacity_mw = st.number_input("Capacity (MW)", min_value=0.0, value=10.0, step=0.5)
    client = st.text_input("Client", "QRT Power")
    offtaker = st.text_input("Offtaker / Buyer", "CEB (example)")
    horizon = st.selectbox("Horizon", ["Short-term", "Mid-term", "Long-term"], index=1)
    extra_context = st.text_area("Extra context (optional)", placeholder="Sites, ports, EPC candidates, constraints, tariffs, etc.")
    uploaded = st.file_uploader("Attach additional context (PDF/TXT/DOCX/CSV)…", accept_multiple_files=True)

    st.divider()
    st.subheader("Finance (quick assumptions)")
    capex = st.number_input("CapEx (USD)", min_value=0.0, value=12_000_000.0, step=100_000.0)
    opex = st.number_input("OpEx annual (USD)", min_value=0.0, value=300_000.0, step=10_000.0)
    energy = st.number_input("Annual energy (MWh)", min_value=0.0, value=21_000.0, step=100.0)
    tariff = st.number_input("Tariff (USD/MWh)", min_value=0.0, value=120.0, step=1.0)

    run_btn = st.button("Run Strategic Analysis", type="primary")

tabs = st.tabs(["📊 Results", "💵 Finance", "🧯 Risk Charts", "🗂 History", "💬 Advisor"])

# --- Run analysis ---
if run_btn:
    with st.spinner("Analyzing…"):
        attachments = {}
        for f in uploaded or []:
            try: attachments[f.name] = f.read().decode("utf-8", errors="ignore")
            except Exception: attachments[f.name] = f.getvalue()
        res = run_strategic_analysis(
            country=country, technology=technology, capacity_mw=capacity_mw,
            client=client, offtaker=offtaker, horizon=horizon,
            user_context=extra_context, attachments=attachments
        )
        st.session_state.res = res
        params = dict(country=country, technology=technology, capacity_mw=capacity_mw,
                      client=client, offtaker=offtaker, horizon=horizon, extra_context=extra_context)
        save_analysis(params, res)

# --- TAB 1: Results ---
with tabs[0]:
    if "res" not in st.session_state:
        st.info("Enter project details in the sidebar and click **Run Strategic Analysis**.")
    else:
        res = st.session_state.res
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Executive Summary"); st.write(res.get("executive_summary", ""))

            st.subheader("PESTEL"); st.table(res.get("pestel"))

            st.subheader("SWOT")
            c3, c4 = st.columns(2)
            with c3:
                st.write("**Strengths**");     st.write("\n".join([f"- {x}" for x in res["swot"].get("strengths", [])]))
                st.write("**Opportunities**"); st.write("\n".join([f"- {x}" for x in res["swot"].get("opportunities", [])]))
            with c4:
                st.write("**Weaknesses**");    st.write("\n".join([f"- {x}" for x in res["swot"].get("weaknesses", [])]))
                st.write("**Threats**");       st.write("\n".join([f"- {x}" for x in res["swot"].get("threats", [])]))

            st.subheader("Legal & Fiscal");           st.write(res.get("legal_fiscal", ""))
            st.subheader("Logistics & Infrastructure"); st.write(res.get("logistics", ""))
            st.subheader("Recommendations");          st.write("\n".join([f"- {x}" for x in res.get("recommendations", [])]))

        with col2:
            st.subheader("Top Risks (auto-prioritized)")
            st.dataframe(res.get("risks"))
            md = to_markdown_report(res)
            st.download_button("⬇️ Download Report (Markdown)", md.encode("utf-8"), file_name="QRT_Strategic_Analysis.md")
            csv_bytes = risks_to_csv_bytes(res.get("risks"))
            st.download_button("⬇️ Download Risks (CSV)", csv_bytes, file_name="QRT_Risks.csv", mime="text/csv")
            pdf_bytes = markdown_to_pdf_bytes(md)
            if pdf_bytes:
                st.download_button("⬇️ Download Report (PDF)", pdf_bytes, file_name="QRT_Strategic_Analysis.pdf", mime="application/pdf")
            else:
                st.caption("PDF export optional (requires wkhtmltopdf on host).")

# --- TAB 2: Finance ---
with tabs[1]:
    st.subheader("Quick Finance KPIs")
    kpis = quick_scenarios(capex, opex, tariff, energy)
    st.metric("IRR (simple)", f"{kpis['IRR']*100:.2f}%")
    st.metric("LCOE (USD/MWh)", f"{kpis['LCOE']:.2f}")
    st.metric("Annual Cashflow (USD)", f"{kpis['AnnualCashflow']:,.0f}")
    st.divider()
    st.write("Sensitivity: Tariff vs IRR")
    tariffs = [tariff*0.8, tariff*0.9, tariff, tariff*1.1, tariff*1.2]
    df_sens = sensitivity_tariff(capex, opex, energy, tariffs)
    st.line_chart(df_sens.set_index("Tariff")["IRR"])

# --- TAB 3: Risk Charts ---
with tabs[2]:
    if "res" in st.session_state:
        st.subheader("Risk Heatmap")
        buf = risk_heatmap(st.session_state.res.get("risks"))
        if buf: st.image(buf)
        st.subheader("PESTEL Radar")
        buf2 = pestel_radar(st.session_state.res.get("pestel"))
        if buf2: st.image(buf2)
    else:
        st.info("Run an analysis to see charts.")

# --- TAB 4: History ---
with tabs[3]:
    st.subheader("Saved Analyses")
    df = list_analyses()
    if df is None or df.empty:
        st.caption("No analyses saved yet.")
    else:
        st.dataframe(df)
        sel = st.number_input("Open analysis ID", min_value=1, step=1)
        if st.button("Load"):
            try:
                row = load_analysis(int(sel))
                st.json({"id": int(sel), "timestamp": row["ts"]})
                st.text_area("Executive Summary", value=row["exec_summary"], height=200)
            except Exception as e:
                st.error(str(e))

# --- TAB 5: Advisor ---
with tabs[4]:
    if "res" not in st.session_state:
        st.info("Run analysis first.")
    else:
        st.subheader("QRT Advisor Chat")
        q = st.text_area("Ask a question about this project or country/regulatory context:")
        if st.button("Ask Advisor"):
            with st.spinner("Thinking..."):
                ctx = json.dumps(st.session_state.res, default=str)[:10000]
                a = ask_advisor(q, ctx)  # pregunta, luego contexto
                st.write(a)

st.markdown("<hr>", unsafe_allow_html=True)
st.caption("© 2025 QRT Strategic Analyst · v2.0 Pro")

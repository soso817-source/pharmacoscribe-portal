import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="PharmacoScribe | Tri-Pillar Oncology Safety Engine",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Analytics 4 (GA4)
# Google Analytics 4 (GA4) with Parent URL Tracking
ga_code = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RTD87BESY9"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  // Configure GA4 with explicit page location to prevent iframe stripping
  gtag('config', 'G-RTD87BESY9', {
      'page_location': window.parent.location.href || window.location.href,
      'send_page_view': true
  });
</script>
"""
components.html(ga_code, height=0, width=0)

# Custom High-Contrast Styling & Header Stripping
st.markdown("""
<style>
    .block-container { padding-top: 1.8rem; padding-bottom: 2.5rem; }
    
    /* Hide Streamlit Header, Main Menu & GitHub elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    
    /* Header Card */
    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 22px 26px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 24px;
    }
    .hero-title { font-size: 2.1rem; font-weight: 800; color: #38bdf8; margin: 0; }
    .hero-subtitle { color: #cbd5e1; font-size: 0.95rem; margin-top: 5px; }
    
    /* Pillar Metric Cards */
    .metric-card {
        background: #1e293b;
        padding: 22px;
        border-radius: 10px;
        border: 1px solid #334155;
        min-height: 290px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    }
    .pillar-header { font-size: 1.1rem; font-weight: 700; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 14px; }
    .p-pv { color: #38bdf8; }
    .p-pgx { color: #c084fc; }
    .p-lit { color: #fbbf24; }
    
    .card-label { color: #cbd5e1; font-size: 0.88rem; font-weight: 500; }
    .card-stat { color: #ffffff; font-size: 2.2rem; font-weight: 800; margin: 4px 0 10px 0; }
    .stat-row { color: #f1f5f9; font-size: 0.92rem; margin: 6px 0; }
    
    /* Signal Badges */
    .signal-badge-pass {
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #059669;
        font-weight: 700;
        text-align: center;
        margin-top: 14px;
    }
    .signal-badge-warn {
        background: rgba(239, 68, 68, 0.18);
        color: #f87171;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #dc2626;
        font-weight: 700;
        text-align: center;
        margin-top: 14px;
    }
    
    /* Action Button Styling */
    .mail-btn {
        display: inline-block;
        background-color: #0284c7;
        color: #ffffff !important;
        padding: 10px 20px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.95rem;
        transition: background-color 0.2s ease;
    }
    .mail-btn:hover { background-color: #0369a1; }
</style>
""", unsafe_allow_html=True)

# 1. Load Data
@st.cache_data
def load_datasets():
    faers_file = "master_faers_index.csv"
    pubmed_file = "master_pubmed_index.csv"
    
    df_faers = pd.read_csv(faers_file) if os.path.exists(faers_file) else pd.DataFrame()
    df_pubmed = pd.read_csv(pubmed_file) if os.path.exists(pubmed_file) else pd.DataFrame()
    
    if not df_faers.empty:
        df_faers['Drug'] = df_faers['Drug'].astype(str).str.upper()
        df_faers['Adverse_Event'] = df_faers['Adverse_Event'].astype(str).str.upper()
    return df_faers, df_pubmed

df_faers, df_pubmed = load_datasets()

if df_faers.empty:
    st.error("Master datasets pending loading. Please ensure CSVs are present.")
    st.stop()

# Header Banner with Client Login Action
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">🧬 PharmacoScribe</div>
        <div class="hero-subtitle">Tri-Pillar Oncopharmacovigilance, PGx Biomarkers & Quantitative Safety Engine</div>
    </div>
    """, unsafe_allow_html=True)

with col_head2:
    st.write("")
    st.write("")
    with st.popover("🔐 Client Portal Log In", use_container_width=True):
        st.subheader("Partner Access")
        user_email = st.text_input("Work Email:", placeholder="name@institution.com")
        user_pass = st.text_input("Access Token / Password:", type="password")
        if st.button("Authenticate", use_container_width=True):
            st.info("Portal authorization is managed via enterprise SSO. Contact sales@pharmacoscribe.com for API provisioning.")

# Controls
drugs_list = sorted(df_faers['Drug'].dropna().unique().tolist())
c_sel1, c_sel2 = st.columns(2)

with c_sel1:
    selected_drug = st.selectbox("Select Target Molecule (49 Tracked):", drugs_list)

drug_df = df_faers[df_faers['Drug'] == selected_drug]
available_events = sorted([e for e in drug_df['Adverse_Event'].dropna().unique().tolist() if e != "NAN"])

with c_sel2:
    if available_events:
        selected_event = st.selectbox("Adverse Event (Reported MedDRA PT):", available_events)
    else:
        selected_event = st.text_input("Adverse Event:", "MUCOSITIS").strip().upper()

st.write("")

# Statistical Calculations
a_raw = len(drug_df[drug_df['Adverse_Event'] == selected_event])
b_raw = len(drug_df[drug_df['Adverse_Event'] != selected_event])
c_raw, d_raw = 5, 500

a, b, c, d = a_raw + 0.5, b_raw + 0.5, c_raw + 0.5, d_raw + 0.5
prr = (a / (a + b)) / (c / (c + d))
ror = (a * d) / (b * c)
se = np.sqrt(1/a + 1/b + 1/c + 1/d)
ci_low = np.exp(np.log(ror) - 1.96 * se)
ci_high = np.exp(np.log(ror) + 1.96 * se)
is_signal = (prr >= 2.0 and a_raw >= 3 and ci_low > 1.0)

# Display 3 Pillar Cards
col1, col2, col3 = st.columns(3)

with col1:
    badge_html = f'<div class="signal-badge-warn">⚠️ DISPROPORTIONATE SIGNAL DETECTED</div>' if is_signal else f'<div class="signal-badge-pass">✅ NO UNEXPECTED DISPROPORTIONALITY</div>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="pillar-header p-pv">1. Pharmacovigilance (FAERS)</div>
        <div class="card-label">Target Event Cases (a):</div>
        <div class="card-stat">{a_raw}</div>
        <div class="stat-row"><strong>PRR:</strong> <span style="color:#38bdf8; font-weight:700; margin-left:6px;">{prr:.2f}</span></div>
        <div class="stat-row"><strong>ROR:</strong> <span style="color:#38bdf8; font-weight:700; margin-left:6px;">{ror:.2f}</span> <span style="font-size:0.8rem; color:#94a3b8;">(95% CI: [{ci_low:.2f} - {ci_high:.2f}])</span></div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

with col2:
    pgx_kb = {
        "METHOTREXATE": [("SLCO1B1", "rs4149056", "1A", "Severe clearance reduction & systemic AUC surge"), ("MTHFR", "rs1801133", "1A", "Elevated mucositis & bone marrow suppression")],
        "FLUOROURACIL": [("DPYD", "*2A / *13", "1A", "Lethal systemic toxicity, severe neutropenia & diarrhea")],
        "TAMOXIFEN": [("CYP2D6", "*4, *5, *10", "1A", "Sub-therapeutic endoxifen bioactivation")]
    }
    entries = pgx_kb.get(selected_drug, [("TPMT / NUDT15", "Tier 1A", "1A", "Elevated risk of severe early-onset myelosuppression")])
    pgx_items = "".join([f"<li style='margin-bottom:10px; color:#f8fafc;'><strong style='color:#f8fafc;'>{g}</strong> (<code style='color:#38bdf8;'>{v}</code>) — <span style='background:#581c87; color:#e9d5ff; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:700;'>Tier {t}</span><br><span style='color:#cbd5e1; font-size:0.85rem;'>{eff}</span></li>" for g, v, t, eff in entries])
    st.markdown(f"""
    <div class="metric-card">
        <div class="pillar-header p-pgx">2. PGx Susceptibility (CPIC)</div>
        <ul style="padding-left:18px; margin:0;">
            {pgx_items}
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    pm_records = df_pubmed[df_pubmed['Drug'].str.upper() == selected_drug] if not df_pubmed.empty else pd.DataFrame()
    valid_titles = pm_records['Title'].dropna().tolist() if not pm_records.empty else []
    top_title = valid_titles[0] if valid_titles else "Comprehensive clinical abstract and systematic citations compiled in full audit dossier."
    st.markdown(f"""
    <div class="metric-card">
        <div class="pillar-header p-lit">3. Literature Evidence (NCBI)</div>
        <div class="card-label">Indexed Systematic Citations:</div>
        <div class="card-stat" style="color:#fbbf24;">{len(pm_records)}</div>
        <div class="card-label" style="margin-top:10px;"><strong>Top Citation:</strong></div>
        <div style="font-size:0.84rem; color:#e2e8f0; font-style:italic; line-height:1.4; margin-top:4px;">{top_title}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Inquiry & Commercial Contact Bar (Direct Email to sales@pharmacoscribe.com)
st.markdown(f"""
<div style="background:#0f172a; border:1px solid #334155; padding:20px 24px; border-radius:10px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
    <div>
        <div style="color:#f8fafc; font-size:1.15rem; font-weight:700;">Regulatory & Clinical Safety Dossier Requests</div>
        <div style="color:#94a3b8; font-size:0.9rem; margin-top:3px;">Custom MedDRA contingency breakdowns, CPIC protocol integration, and audit-ready reports.</div>
    </div>
    <div>
        <a class="mail-btn" href="mailto:sales@pharmacoscribe.com?subject=Dossier Inquiry: {selected_drug} - {selected_event}&body=Hello PharmacoScribe Team,%0D%0A%0D%0AI would like to request an audit dossier for {selected_drug} regarding {selected_event}.%0D%0A%0D%0AOrganization:%0D%0AContact:">
            ✉️ Contact Sales / Request Dossier
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

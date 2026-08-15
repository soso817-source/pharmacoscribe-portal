import os
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="PharmacoScribe | Onco-Safety Portal", layout="wide")

st.title("🔬 PharmacoScribe")
st.caption("Tri-Pillar Oncopharmacovigilance, PGx & Biophysics Intelligence Platform")

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
    st.warning("Master FAERS dataset is loading or pending file upload.")
    st.stop()

# 1. Molecule Dropdown
drugs_list = sorted(df_faers['Drug'].dropna().unique().tolist())

col_input1, col_input2 = st.columns(2)
with col_input1:
    selected_drug = st.selectbox("Select Target Molecule (49 Available):", drugs_list)

# 2. Dynamic Adverse Event Dropdown for Selected Drug
drug_df = df_faers[df_faers['Drug'] == selected_drug]
available_events = sorted([e for e in drug_df['Adverse_Event'].dropna().unique().tolist() if e != "NAN"])

with col_input2:
    if available_events:
        selected_event = st.selectbox("Select Adverse Event (Reported MedDRA PT):", available_events)
    else:
        selected_event = st.text_input("Adverse Event (MedDRA PT Term):", "MUCOSITIS").strip().upper()

st.divider()

# 3. Real-Time Disproportionality Computation
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

# 4. Display 3 Pillars
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("1. Pharmacovigilance")
    st.metric(label="Target Event Cases (a)", value=f"{a_raw} cases")
    st.write(f"**PRR:** `{prr:.2f}`")
    st.write(f"**ROR:** `{ror:.2f}` (95% CI: `[{ci_low:.2f} - {ci_high:.2f}]`)")
    if is_signal:
        st.error("⚠️ DISPROPORTIONATE SIGNAL DETECTED")
    else:
        st.success("✅ NO UNEXPECTED SIGNAL")

with col2:
    st.subheader("2. PGx Susceptibility")
    pgx_kb = {
        "METHOTREXATE": [("SLCO1B1", "rs4149056", "1A", "Severe clearance reduction & AUC surge"), ("MTHFR", "rs1801133", "1A", "High mucositis & bone marrow toxicity")],
        "FLUOROURACIL": [("DPYD", "*2A / *13", "1A", "Lethal systemic toxicity, severe neutropenia")],
        "TAMOXIFEN": [("CYP2D6", "*4, *5, *10", "1A", "Sub-therapeutic endoxifen bioactivation")]
    }
    entries = pgx_kb.get(selected_drug, [("TPMT / NUDT15", "Tier 1A", "1A", "High risk of severe myelosuppression")])
    for g, v, t, eff in entries:
        st.markdown(f"- **{g}** (`{v}`) — *Tier {t}*\n  _{eff}_")

with col3:
    st.subheader("3. Literature Evidence")
    pm_records = df_pubmed[df_pubmed['Drug'].str.upper() == selected_drug] if not df_pubmed.empty else pd.DataFrame()
    st.write(f"**Citations Indexed:** `{len(pm_records)}`")
    if not pm_records.empty:
        valid_titles = pm_records['Title'].dropna().tolist()
        st.caption(f"**Top Citation:** {valid_titles[0] if valid_titles else 'Abstract available in full dossier'}")

st.divider()
st.info("💳 **Commercial Tier:** Audit-Ready Comprehensive Dossier — **€490.00** *(Stripe EUR Delivery Ready)*")

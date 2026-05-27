"""
PaperShield — Streamlit UI
Place this file in the root of your project (same level as agent.py, ingest.py, etc.)
Run: streamlit run ui.py
"""
 
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
 
load_dotenv()
 
# Import your existing modules directly — no API layer needed
from database import setup_database
from ingest import ingest_pdf
from agent import run_ask, run_scan
 
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PaperShield",
    page_icon="🛡️",
    layout="centered"
)
 
# ── Minimal styling ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  .risk-high   { background:#3b0f0f; border-left:4px solid #f87171; padding:12px 16px; margin:8px 0; border-radius:2px; }
  .risk-medium { background:#3b2a0f; border-left:4px solid #fbbf24; padding:12px 16px; margin:8px 0; border-radius:2px; }
  .risk-low    { background:#0f2d1a; border-left:4px solid #4ade80; padding:12px 16px; margin:8px 0; border-radius:2px; }
  .risk-label  { font-size:11px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; margin-bottom:4px; }
  .disclaimer  { font-size:12px; color:#888; border-top:1px solid #333; padding-top:12px; margin-top:16px; }
</style>
""", unsafe_allow_html=True)
 
# ── Header ───────────────────────────────────────────────────────────────────
st.title("🛡️ PaperShield")
st.caption("AI-powered contract risk analyzer — upload a contract, ask questions, or run a full risk scan.")
st.divider()
 
# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.subheader("1 · Upload a Contract")
 
uploaded_file = st.file_uploader("Choose a PDF contract", type=["pdf"])
 
if uploaded_file:
    doc_id = os.path.splitext(uploaded_file.name)[0]  # e.g. "lease" from "lease.pdf"
    st.session_state["doc_id"] = doc_id
 
    if st.button("📥 Index Contract"):
        with st.spinner(f"Parsing and embedding '{uploaded_file.name}'..."):
            try:
                # Save uploaded file to a temp path, then call your existing ingest_pdf()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
 
                setup_database()
                ingest_pdf(tmp_path, doc_id)
                os.unlink(tmp_path)
 
                st.success(f"✅ '{uploaded_file.name}' indexed as **{doc_id}**. Ready to query.")
                st.session_state["indexed"] = True
            except Exception as e:
                st.error(f"Upload failed: {e}")
 
st.divider()
 
# ── Step 2: Ask a Question ────────────────────────────────────────────────────
st.subheader("2 · Ask a Question")
 
# Let users type a doc_id manually if they already uploaded via CLI
doc_id_input = st.text_input(
    "Contract name",
    value=st.session_state.get("doc_id", ""),
    placeholder="e.g.  lease  (filename without .pdf)"
)
question = st.text_area("Your question", placeholder="What is the late fee? / Can the landlord enter without notice?")
 
if st.button("💬 Ask"):
    if not doc_id_input.strip():
        st.warning("Enter a contract name first.")
    elif not question.strip():
        st.warning("Type a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                result = run_ask(doc_id_input.strip(), question.strip())
 
                st.markdown("**Answer**")
                st.write(result.get("answer", "—"))
 
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Cited Clause**")
                    st.write(result.get("cited_clause", "—"))
                with col2:
                    st.markdown("**Section**")
                    st.write(result.get("section", "—"))
 
                st.markdown(f'<p class="disclaimer">{result.get("disclaimer","")}</p>', unsafe_allow_html=True)
 
            except Exception as e:
                st.error(f"Error: {e}")
 
st.divider()
 
# ── Step 3: Risk Scan ─────────────────────────────────────────────────────────
st.subheader("3 · Full Risk Scan")
 
scan_doc_id = st.text_input(
    "Contract name to scan",
    value=st.session_state.get("doc_id", ""),
    placeholder="e.g.  lease",
    key="scan_doc_id"
)
 
if st.button("🔍 Run Risk Scan"):
    if not scan_doc_id.strip():
        st.warning("Enter a contract name.")
    else:
        with st.spinner("Scanning contract and searching legal context (this may take ~30s)..."):
            try:
                risks = run_scan(scan_doc_id.strip())
 
                if not risks:
                    st.success("No significant risks detected.")
                else:
                    # Summary badges
                    high   = sum(1 for r in risks if r["risk_level"] == "high")
                    medium = sum(1 for r in risks if r["risk_level"] == "medium")
                    low    = sum(1 for r in risks if r["risk_level"] == "low")
 
                    c1, c2, c3 = st.columns(3)
                    c1.metric("🔴 High",   high)
                    c2.metric("🟡 Medium", medium)
                    c3.metric("🟢 Low",    low)
 
                    st.markdown(f"**{len(risks)} risk(s) found** — review each below:")
 
                    # Render each risk flag
                    for i, risk in enumerate(risks, 1):
                        level = risk.get("risk_level", "low")
                        css_class = f"risk-{level}"
                        label_color = {"high": "#f87171", "medium": "#fbbf24", "low": "#4ade80"}.get(level, "#888")
 
                        with st.expander(f"Risk {i} · [{level.upper()}] · {risk.get('clause','')[:80]}..."):
                            st.markdown(f'<p class="risk-label" style="color:{label_color}">{level.upper()} RISK</p>', unsafe_allow_html=True)
 
                            st.markdown("**Clause**")
                            st.write(risk.get("clause", "—"))
 
                            st.markdown("**Section**")
                            st.write(risk.get("section", "—"))
 
                            st.markdown("**Plain English**")
                            st.write(risk.get("plain_english", "—"))
 
                            st.markdown("**Legal Context**")
                            st.write(risk.get("legal_context", "—"))
 
                            st.markdown("**Recommendation**")
                            st.write(risk.get("recommendation", "—"))
 
                        st.markdown(f'<p class="disclaimer">{risk.get("disclaimer","")}</p>', unsafe_allow_html=True)
 
            except Exception as e:
                st.error(f"Scan failed: {e}")
import streamlit as st
import re
import io
from docx import Document
import anthropic

st.set_page_config(page_title="SmartCite — Evidence Audit", page_icon="🔎", layout="wide")

st.title("🔎 SmartCite — Evidence Audit")
st.caption("v1: Claim–citation alignment check. Upload a manuscript and paste the abstracts of what it cites.")

# ── API key ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Anthropic API key", type="password",
                             help="Get one at console.anthropic.com. Stored only for this session, never saved.")
    st.caption("For a deployed app, set this as a Streamlit secret (ANTHROPIC_API_KEY) instead of typing it each time.")
    model = st.selectbox("Model", ["claude-sonnet-4-6", "claude-haiku-4-5-20251001"], index=0)

# ── helpers ───────────────────────────────────────────────────────────────

CITATION_PATTERN = re.compile(r'\(([A-Z][a-zA-Z\-]+(?:\s+et al\.?)?,?\s*\d{4}[a-z]?)\)|\[(\d+(?:,\s*\d+)*)\]')

def extract_docx_text(file) -> str:
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def find_citation_sentences(text: str):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    hits = []
    for s in sentences:
        if CITATION_PATTERN.search(s):
            hits.append(s.strip())
    return hits

def audit_claim(client, model, sentence: str, evidence: str):
    prompt = f"""You are auditing a scientific manuscript sentence against the abstract(s) of the paper(s) it cites.

MANUSCRIPT SENTENCE (with citation):
"{sentence}"

CITED SOURCE ABSTRACT(S)/TEXT PROVIDED BY THE AUTHOR:
"{evidence}"

Assess strictly based on the provided abstract text. Respond in this exact format:

ALIGNMENT: [Supported / Partially Supported / Not Supported / Cannot Assess]
OVERCLAIMING: [Yes / No] - one sentence explaining why
MISSING CAVEATS: [Yes / No] - one sentence naming any caveat (sample size, species, model system) present in the source but absent from the claim
JUSTIFICATION NOTE: one or two sentences an author could paste into a response-to-reviewers letter explaining why this citation supports this claim (or noting that it doesn't)
"""
    resp = client.messages.create(
        model=model,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text

# ── UI ────────────────────────────────────────────────────────────────────

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload manuscript")
    uploaded = st.file_uploader("Word document (.docx)", type=["docx"])

with col2:
    st.subheader("2. Paste cited source text")
    st.caption("For v1: paste the abstract(s) of the paper(s) referenced in the sentence you want to check. Full-PDF grounding is a planned upgrade — see the roadmap on the SmartCite page.")
    evidence_text = st.text_area("Abstract(s) / source text", height=200,
                                  placeholder="Paste the abstract of the cited paper here...")

st.divider()

if uploaded:
    manuscript_text = extract_docx_text(uploaded)
    citation_sentences = find_citation_sentences(manuscript_text)

    st.subheader(f"3. Citation-bearing sentences found: {len(citation_sentences)}")

    if not citation_sentences:
        st.info("No sentences with a recognisable citation pattern — e.g. (Author, Year) or [1] — were found.")
    else:
        selected = st.selectbox("Pick a sentence to audit", citation_sentences)

        if st.button("Run audit", type="primary", disabled=not (api_key and evidence_text)):
            if not api_key:
                st.error("Add your Anthropic API key in the sidebar.")
            elif not evidence_text:
                st.error("Paste the cited source's abstract/text to check against.")
            else:
                with st.spinner("Checking claim against source..."):
                    try:
                        client = anthropic.Anthropic(api_key=api_key)
                        result = audit_claim(client, model, selected, evidence_text)
                        st.success("Audit complete")
                        st.markdown("### Result")
                        st.code(result, language=None)
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")
else:
    st.info("Upload a .docx manuscript to begin.")

st.divider()
st.caption(
    "Scope: this flags potential evidence-alignment issues for the author's own review. "
    "It does not replace peer review, editorial judgment, or the author's responsibility "
    "for the accuracy of their claims."
)

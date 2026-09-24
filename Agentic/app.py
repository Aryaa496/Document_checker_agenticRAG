# app.py
#
# Streamlit frontend for the compliance checker. Handles file upload,
# calls document_checker.check_document(), and renders the structured
# results as a readable summary + detailed table, instead of raw JSON.

import streamlit as st
import pandas as pd
import io

from document_checker import check_document

st.set_page_config(page_title="UK Visa Compliance Checker", layout="wide")

st.title("UK Visa Sponsorship Compliance Checker")
st.write(
    "Upload a job offer letter to check its clauses against UK Skilled Worker "
    "and Graduate visa requirements."
)

# --- Sidebar: quick config, useful while you're still tuning this ---
with st.sidebar:
    st.header("Settings")
    max_workers = st.slider(
        "Concurrent checks", min_value=1, max_value=3, value=1,
        help="Keep at 1 on Groq's free tier to avoid rate limits."
    )
    st.caption(
        "Each clause runs through a full retrieve → judge → rewrite → answer "
        "loop, so larger documents will take a while on the free tier."
    )

# --- File upload ---
uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf"])

# Also allow pasting text directly, useful for quick testing
with st.expander("Or paste document text directly"):
    pasted_text = st.text_area("Paste job offer text here", height=200)


def extract_text(file) -> str:
    if file.type == "application/pdf":
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        return file.read().decode("utf-8")


document_text = None
if uploaded_file is not None:
    document_text = extract_text(uploaded_file)
elif pasted_text.strip():
    document_text = pasted_text

if document_text:
    with st.expander("Preview document text"):
        st.text(document_text)

    if st.button("Run compliance check", type="primary"):
        with st.spinner("Extracting clauses and checking against the rulebook — this can take a minute..."):
            results = check_document(document_text, max_workers=max_workers)

        if not results:
            st.warning("No checkable clauses were extracted from this document.")
        else:
            df = pd.DataFrame(results)

            # --- Summary stats at the top ---
            st.subheader("Summary")
            col1, col2, col3, col4 = st.columns(4)
            total = len(df)
            compliant = (df["status"] == "COMPLIANT").sum()
            non_compliant = (df["status"] == "NON_COMPLIANT").sum()
            unclear = (df["status"] == "UNCLEAR").sum()

            col1.metric("Total clauses checked", total)
            col2.metric("Compliant", compliant)
            col3.metric("Non-compliant", non_compliant, delta=None,
                        delta_color="inverse" if non_compliant > 0 else "off")
            col4.metric("Unclear", unclear)

            if non_compliant > 0:
                st.error(
                    f"⚠️ {non_compliant} clause(s) appear to be non-compliant. "
                    "Review the flagged items below before proceeding."
                )
            elif unclear > 0:
                st.warning(
                    f"{unclear} clause(s) could not be conclusively checked. "
                    "Manual review recommended for these."
                )
            else:
                st.success("All checked clauses appear compliant.")

            # --- Status badge helper ---
            def status_badge(status: str) -> str:
                colors = {
                    "COMPLIANT": "🟢",
                    "NON_COMPLIANT": "🔴",
                    "UNCLEAR": "🟡",
                }
                return f"{colors.get(status, '⚪')} {status}"

            # --- Detailed results, one expandable card per clause ---
            st.subheader("Detailed findings")
            for _, row in df.iterrows():
                with st.expander(f"{status_badge(row['status'])} — {row['clause'][:80]}"):
                    st.markdown(f"**Clause:** {row['clause']}")
                    st.markdown(f"**Status:** {status_badge(row['status'])}")
                    if row.get("applicable_requirement"):
                        st.markdown(f"**Applicable requirement:** {row['applicable_requirement']}")
                    if row.get("document_value") or row.get("required_value"):
                        st.markdown(
                            f"**Document states:** {row.get('document_value', '—')}  \n"
                            f"**Rule requires:** {row.get('required_value', '—')}"
                        )
                    st.markdown(f"**Reason:** {row['reason']}")
                    if row.get("rule"):
                        st.caption(f"Rule reference: {row['rule']}")
                    st.caption(f"Attempts taken: {row.get('attempts', '—')}")

            # --- Full table + download ---
            st.subheader("Full results table")
            display_df = df[["clause", "status", "rule", "reason"]].rename(columns={
                "clause": "Clause",
                "status": "Status",
                "rule": "Rule cited",
                "reason": "Reason",
            })
            st.dataframe(display_df, use_container_width=True)

            csv = df.to_csv(index=False)
            st.download_button(
                "Download full results as CSV",
                csv,
                "compliance_check_results.csv",
                "text/csv",
            )
else:
    st.info("Upload a document or paste text above to get started.")
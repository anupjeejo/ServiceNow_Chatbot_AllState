import requests
import streamlit as st
from docx import Document
from pypdf import PdfReader

CREATE_INCIDENT_API_URL = "http://localhost:8000/chat"
INCIDENT_QUERY_API_URL = "http://localhost:8000/incident-query"
KB_DOCUMENT_API_URL = "http://localhost:8000/kb-document"


def _extract_text_from_upload(uploaded_file) -> str:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")

    if file_name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    if file_name.endswith(".docx"):
        doc = Document(uploaded_file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    return ""

st.set_page_config(
    page_title="ServiceNow AI Copilot",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("🧠 ServiceNow AI Copilot")
st.caption("AI-powered incident creation and incident-specific Q&A")

if "create_messages" not in st.session_state:
    st.session_state.create_messages = []

if "query_messages" not in st.session_state:
    st.session_state.query_messages = []

create_tab, query_tab = st.tabs(["Create Incident", "Incident Q&A"])

with create_tab:
    st.subheader("Create an incident")
    st.caption("Describe your issue to create a new ServiceNow incident and get a suggested workaround.")

    for msg in st.session_state.create_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input(
        "Describe your issue (e.g., VPN keeps disconnecting)...",
        key="create_incident_chat_input",
    )

    if user_input:
        st.session_state.create_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing previous incidents and creating ticket..."):
                try:
                    resp = requests.post(
                        CREATE_INCIDENT_API_URL,
                        json={"message": user_input},
                        timeout=200,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    assistant_md = f"""
                        ✅ **Ticket Created Successfully**

                        **Ticket Number:** `{data['ticket_number']}`

                        ---
                        ### 📌 Suggested Workaround
                        {data['workaround']}

                        ---
                        ### 🧾 Summary
                        {data['summary']}

                        **Confidence:** `{data['confidence']}`  
                        **Based on past incidents:** {", ".join(data["based_on_incidents"])}
                    """
                    st.markdown(assistant_md)

                    st.session_state.create_messages.append(
                        {"role": "assistant", "content": assistant_md}
                    )

                except Exception as e:
                    error_msg = f"❌ Unable to process the request.\n\nError: `{e}`"
                    st.markdown(error_msg)
                    st.session_state.create_messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

with query_tab:
    st.subheader("Ask about an existing incident")
    st.caption(
        "Provide an incident number, optionally add general KB documents (txt/pdf/word), and ask follow-up questions."
    )

    incident_number = st.text_input(
        "Incident number",
        placeholder="e.g., INC0012345",
        key="incident_number_input",
    )

    with st.expander("📘 General KB document library (optional)", expanded=False):
        kb_name = st.text_input(
            "KB document name",
            placeholder="e.g., Payments RCA Playbook",
            key="kb_name_input",
        )
        kb_file = st.file_uploader(
            "Upload KB file (.txt, .pdf, .docx)",
            type=["txt", "pdf", "docx"],
            key="kb_file",
        )
        uploaded_kb_text = ""
        if kb_file is not None:
            try:
                uploaded_kb_text = _extract_text_from_upload(kb_file)
            except Exception as e:
                st.error(f"Unable to parse uploaded file: `{e}`")

        kb_input = st.text_area(
            "Paste KB content",
            value=uploaded_kb_text,
            height=180,
            placeholder=(
                "Example: Root cause, RCA steps, validation checklist, rollback notes, "
                "or known error references."
            ),
        )
        save_kb = st.button("Save KB to vector store")
        if save_kb:
            kb_text = kb_input.strip()
            if not kb_text:
                st.warning("Please provide KB content before saving.")
            else:
                try:
                    kb_resp = requests.post(
                        KB_DOCUMENT_API_URL,
                        json={
                            "kb_name": kb_name.strip() if kb_name.strip() else (kb_file.name if kb_file else None),
                            "kb_document": kb_text,
                        },
                        timeout=200,
                    )
                    kb_resp.raise_for_status()
                    saved_name = kb_resp.json().get("kb_name", "General KB Document")
                    st.success(f"KB `{saved_name}` saved in vector store.")
                except Exception as e:
                    st.error(f"Unable to save KB document: `{e}`")

    with st.form("incident_query_form", clear_on_submit=True):
        query_input = st.text_input(
            "Query",
            placeholder="Ask a question about this incident...",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Ask")

    if submitted:
        if not incident_number.strip():
            st.warning("Please enter an incident number before asking a question.")
        elif not query_input.strip():
            st.warning("Please enter a query before submitting.")
        else:
            user_md = f"**Incident:** `{incident_number.strip()}`\n\n{query_input.strip()}"
            st.session_state.query_messages.append({"role": "user", "content": user_md})

            with st.spinner("Looking up incident and preparing answer..."):
                try:
                    resp = requests.post(
                        INCIDENT_QUERY_API_URL,
                        json={
                            "incident_number": incident_number.strip(),
                            "question": query_input.strip(),
                        },
                        timeout=200,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    assistant_md = data["answer"]
                    kb_refs = data.get("kb_references") or []
                    if kb_refs:
                        assistant_md = (
                            f"{assistant_md}\n\n"
                            f"**Referenced KB document(s):** {', '.join(f'`{name}`' for name in kb_refs)}"
                        )
                    st.session_state.query_messages.append(
                        {"role": "assistant", "content": assistant_md}
                    )
                except Exception as e:
                    error_msg = f"❌ Unable to answer your question.\n\nError: `{e}`"
                    st.session_state.query_messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

    # for msg in reversed(st.session_state.query_messages):
    for msg in st.session_state.query_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

st.divider()
st.caption(
    "This copilot uses historical ServiceNow incidents and semantic similarity "
    "to suggest safe, temporary workarounds and answer incident-specific questions."
)

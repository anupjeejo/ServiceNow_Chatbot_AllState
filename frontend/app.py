import requests
import streamlit as st

CREATE_INCIDENT_API_URL = "http://localhost:8000/chat"
INCIDENT_QUERY_API_URL = "http://localhost:8000/incident-query"

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
    st.caption("Provide an incident number and ask follow-up questions in chat format.")

    incident_number = st.text_input(
        "Incident number",
        placeholder="e.g., INC0012345",
        key="incident_number_input",
    )

    for msg in st.session_state.query_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    query_input = st.chat_input(
        "Ask a question about this incident...",
        key="incident_query_chat_input",
    )

    if query_input:
        if not incident_number.strip():
            st.warning("Please enter an incident number before asking a question.")
        else:
            user_md = f"**Incident:** `{incident_number.strip()}`\n\n{query_input}"
            st.session_state.query_messages.append({"role": "user", "content": user_md})
            with st.chat_message("user"):
                st.markdown(user_md)

            with st.chat_message("assistant"):
                with st.spinner("Looking up incident and preparing answer..."):
                    try:
                        resp = requests.post(
                            INCIDENT_QUERY_API_URL,
                            json={
                                "incident_number": incident_number.strip(),
                                "question": query_input,
                            },
                            timeout=200,
                        )
                        resp.raise_for_status()
                        data = resp.json()

                        assistant_md = f"{data['answer']}"
                        st.markdown(assistant_md)
                        st.session_state.query_messages.append(
                            {"role": "assistant", "content": assistant_md}
                        )
                    except Exception as e:
                        error_msg = f"❌ Unable to answer your question.\n\nError: `{e}`"
                        st.markdown(error_msg)
                        st.session_state.query_messages.append(
                            {"role": "assistant", "content": error_msg}
                        )

st.divider()
st.caption(
    "This copilot uses historical ServiceNow incidents and semantic similarity "
    "to suggest safe, temporary workarounds and answer incident-specific questions."
)

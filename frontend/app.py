# frontend/app.py
import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"

st.set_page_config(
    page_title="ServiceNow AI Copilot",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("🧠 ServiceNow AI Copilot")
st.caption("AI-powered incident creation with workaround suggestions from past incidents")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Describe your issue (e.g., VPN keeps disconnecting)...")

if user_input:
    # Add user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call backend
    with st.chat_message("assistant"):
        with st.spinner("Analyzing previous incidents and creating ticket..."):
            try:
                resp = requests.post(
                    API_URL,
                    json={"message": user_input},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()

                # Main response
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

                # Save assistant message
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_md}
                )

            except Exception as e:
                error_msg = f"❌ Unable to process the request.\n\nError: `{e}`"
                st.markdown(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

# Footer
st.divider()
st.caption(
    "This copilot uses historical ServiceNow incidents and semantic similarity "
    "to suggest safe, temporary workarounds."
)

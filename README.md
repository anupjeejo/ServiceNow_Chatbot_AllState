# ServiceNow AI Copilot 🤖🛠️

An **AI-powered ITSM copilot** that creates ServiceNow incidents, suggests **workarounds and summaries** from past resolved incidents, and now supports **incident-specific Q&A with reusable KB documents**.

This project is built for enterprise-style workflows and runs with **local LLM inference via Ollama**.

---

## ✨ Latest Features

- ✅ **Natural-language incident creation** that converts user messages into structured incident payloads.
- 🧠 **Semantic retrieval over resolved incidents** using FAISS + sentence-transformer embeddings.
- 🎯 **Automatic assignment group prediction** based on the most common group in similar historical incidents.
- 🔧 **AI-generated workaround suggestions** with confidence labels (`high`, `medium`, `low`).
- 🧾 **AI summary generation** from retrieved historical incidents.
- 💬 **Incident Q&A mode** for existing tickets (`/incident-query`) with incident-aware answers.
- 📘 **KB document library support** (`/kb-document`) to store reusable KB content in the vector store.
- 📄 **KB file ingestion in UI** for `.txt`, `.pdf`, and `.docx` files.
- 🗂️ **Persistent vector store storage** (`backend/data/vector_store`) so indexed content survives restarts.
- 🔁 **Multi-agent orchestration** with LangGraph (parse → retrieve → assign → workaround → summary).
- 🔐 **Local/private model inference** using Ollama.

---

## 🏗️ Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **LLM:** Ollama
- **Vector Search:** FAISS
- **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **Workflow Engine:** LangGraph
- **ITSM Platform:** ServiceNow REST API

---

## 📁 Project Structure

```text
ServiceNow_Chatbot_AllState/
├── backend/
│   ├── app/
│   │   ├── agents/              # Parser, retrieval, assignment, workaround, summary agents
│   │   ├── api/routes.py        # /chat, /incident-query, /kb-document
│   │   ├── core/                # Config, logging, vector bootstrap
│   │   ├── graph/workflow.py    # LangGraph orchestration
│   │   ├── schemas/             # Request/response models
│   │   └── services/            # ServiceNow, Ollama, vector store clients
│   └── data/vector_store/       # Persisted FAISS index + metadata
├── frontend/
│   └── app.py                   # Streamlit UI (Create Incident + Incident Q&A tabs)
└── README.md
```

---

## ⚙️ Prerequisites

- Python **3.10+**
- ServiceNow developer instance
- Ollama installed locally

---

## 🔐 Environment Variables (`.env`)

```bash
SN_INSTANCE=https://devXXXX.service-now.com
SN_USER=api_user
SN_PASSWORD=api_password
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2
```

---

## 🚀 Setup

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Frontend

```bash
cd frontend
pip install -r requirements.txt
```

---

## ▶️ Run the App

### Start backend (FastAPI)

```bash
cd backend
uvicorn app.main:app --reload
```

### Start frontend (Streamlit)

```bash
cd frontend
streamlit run app.py
```

---

## 🔌 API Endpoints

### `POST /chat`
Create a ServiceNow incident from natural language and return:
- ticket number
- workaround
- confidence
- summary
- historical incident references

### `POST /incident-query`
Ask a question about an existing incident number. The backend retrieves incident details + matching KB context and returns an incident-grounded answer.

### `POST /kb-document`
Save or update a named KB document into the vector store for future incident Q&A retrieval.

---

## 🖥️ UI Capabilities

- **Create Incident tab**
  - Chat-style issue submission
  - AI workaround + summary display
  - Ticket number and historical references

- **Incident Q&A tab**
  - Query by incident number
  - Optional KB document upload (`.txt/.pdf/.docx`) or paste
  - Save KB into vector store and reference it in later answers

---

## 🧪 Notes

- Historical incidents are bootstrapped into the vector store from closed ServiceNow tickets.
- KB entries are stored with metadata and can be filtered during search.
- If no historical incidents are found, the app returns a safe fallback workaround and summary.

---

## Sample App Screen-shots

<img width="777" height="862" alt="image" src="https://github.com/user-attachments/assets/70edf215-1e6e-43bb-9758-1a51388c786f" />

---

<img width="1652" height="555" alt="image" src="https://github.com/user-attachments/assets/f0a9cfa6-55bc-4adf-9cd1-4e5123fe2809" />

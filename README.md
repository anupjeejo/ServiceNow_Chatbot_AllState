# ServiceNow AI Copilot 🤖🛠️

An **AI-powered ITSM copilot** that creates ServiceNow incidents and automatically suggests **workarounds and summaries** by learning from **previous resolved incidents** using **semantic similarity (FAISS)** and **multi-agent reasoning (LangGraph)**.
This project is designed for **enterprise, production-grade environments** and runs entirely with **local LLMs (Ollama)**.

---

## ✨ Key Features

- ✅ Create ServiceNow incidents from **natural language**
- 🧠 Retrieve similar past incidents using **FAISS vector similarity**
- 🔧 Suggest **safe, temporary workarounds** based on **historical resolutions**
- 🧾 Generate **management-ready summaries**
- 🎯 Auto-assign **Assignment Group** using past resolved incidents
- 🔐 Local & secure LLM inference using **Ollama**
- 🔁 Multi-agent orchestration using **LangGraph**
- 💬 Chat-style UI with **Streamlit**

---

## 🏗️ Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **LLM:** Ollama
- **Vector Search:** FAISS
- **Embeddings:** Sentence Transformers
- **Workflow Engine:** LangGraph
- **ITSM Platform:** ServiceNow

---


## 📁 Project Structure (Simplified)
servicenow-ai-agent/
├── backend/ # FastAPI + AI agents + FAISS
├── frontend/ # Streamlit chat UI
├── docs/
├── .gitignore
└── README.md

---

## ⚙️ Prerequisites
- Python **3.10+**
- ServiceNow developer instance
- Ollama installed locally

---

## .env example
SN_INSTANCE=https://devXXXX.service-now.com
SN_USER=api_user
SN_PASSWORD=api_password
OLLAMA_URL=http://localhost:11434/api/generate

---

## Backend Setup
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

---

## Frontend Setup
cd frontend
pip install -r requirements.txt

---

## Start Backend (FastAPI)
uvicorn app.main:app --reload

---

## Start Frontend (Streamlit)
streamlit run app.py

## Sample App Screen-shots

<img width="777" height="862" alt="image" src="https://github.com/user-attachments/assets/70edf215-1e6e-43bb-9758-1a51388c786f" />

---

<img width="1652" height="555" alt="image" src="https://github.com/user-attachments/assets/f0a9cfa6-55bc-4adf-9cd1-4e5123fe2809" />


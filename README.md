# Data Analyst Depth (DAD) 📊

> **The ultimate modern platform for automated data analysis, bridging the gap between raw data files and production-grade AI insights.**

Data Analyst Depth (DAD) is a full-stack, AI-powered internal workspace built to transform raw CSVs, Excel, and JSON data into actionable insights, interactive Recharts visualizations, and formatted reports. 

Powered by **Google Gemini** & **OpenAI GPT-4o**, DAD completely isolates data processing via isolated thread-pools and local DuckDB logic, providing a flawless zero-latency UI while chewing through massive datasets.

---

## 🚀 Key Features

* **AI Chat Interface**: Ask plain-english questions about your datasets. The integrated agent engine will generate fully-sandboxed Pandas verification scripts to answer dynamically.
* **Smart Cleaning & Formatting**: Standardize dates, handle missing variables, and auto-drop empty columns directly inside the upload pipeline.
* **Dynamic AI Overrides**: Connect to standard server keys OR dynamically input your own `API Key` and model choice (`Gemini 2.0 Flash`, `GPT-4o`) directly in the Chat interface.
* **Persistent Workspaces**: Save context natively via local SQLAlchemy SQLite database mapping and the raw binary `data_lake` cache.

---

## 🛠 Tech Stack

Data Analyst Depth utilizes a high-octane modern deployment strategy.

### Backend
* **Python 3.10+ / FastAPI**: Ultra-fast asynchronous framework
* **SQLAlchemy / aiosqlite**: Production-ready deterministic DB ORM.
* **Pandas / DuckDB**: Efficient DataFrame processing
* **Google Generative AI / OpenAI**: LLM Integration
* **Uvicorn**: ASGI Native Server

### Frontend
* **React 18**: Dynamic UI
* **Tailwind CSS**: Modern utility component styling
* **Recharts**: Beautiful data visualizations
* **Axios**: Network interfacing

---

## 🗄️ Documentation

To see under the hood, view the comprehensive functional business docs:
* 📄 [Business Requirements Document (BRD)](./docs/BRD.md)
* 📐 [Platform Architecture & DFD](./docs/ARCHITECTURE.md)

---

## ⚙️ Running Locally

### 1. Prerequisites
- Python 3.10+
- Node.js & npm

### 2. Quick Setup

```bash
# 1. Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate 
pip install -r requirements.txt

# Run migrations to generate local data_analyst.db
alembic upgrade head

# Boot Server
uvicorn server:app --reload --port 8000

# ----------------- #

# 2. Frontend Setup
cd frontend
npm install

# Boot React Client
npm start
```

### 3. Native File Usage
All datasets are securely saved to `./backend/data_lake/` and database configuration maps natively to `./backend/data_analyst.db`.

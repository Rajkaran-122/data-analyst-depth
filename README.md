# Data Bridge / Data Analyst Depth

A full-stack **Data Bridge platform** built on top of the TDS Data Analyst agent.  
It lets you:

- Ask natural language questions to an analysis agent
- Upload datasets (CSV/XLSX/JSON) for analysis
- Inspect dataset schemas
- Monitor activity & basic metrics
- Test data connectors
- Persist activity logs to MongoDB

The app runs as a React frontend and FastAPI backend, with services managed by `supervisor`.

---

## 🔧 Tech Stack

- **Frontend**: React + Tailwind CSS  
- **Backend**: FastAPI (Python)  
- **Database**: MongoDB (via `motor`)  
- **Data / Analytics**:
  - `pandas`, `duckdb`
  - `matplotlib`, `seaborn` for plots
  - Optional LLM (Gemini), via `agent_core.py`
- **Process Management**: `supervisor`

---

## 🚀 Core Features

### 1. Workspace (Interactive Analytics)

- Ask questions in plain English:
  - POST `/api/analyze`
  - Body: `{ "question": "...", "context": {} }`
- Upload a dataset and analyze:
  - POST `/api/` (multipart)
  - Fields:  
    - `questions.txt` → plain text question  
    - one or more data files: `data.csv`, `nodes.csv`, etc.

The backend:
- Uses Gemini/LLM path if `GOOGLE_API_KEY` is set
- Falls back to **offline heuristics** (sales analysis, DuckDB demo, Wikipedia summary) if no LLM is configured

### 2. Schema Inspection

- Endpoint: `POST /api/inspect-schema`
- Multipart field: `file=@yourfile.csv`
- Returns:
  - `filename`
  - `row_count`
  - `columns` (name + dtype)
  - `preview` (first rows)

The frontend shows this in a compact **Schema Preview** table.

### 3. Connectors

Static connectors registry:

- `csv-upload` (active)
- `http-api` (planned)
- `database` (planned)

APIs:

- `GET /api/connectors` → list connectors
- `POST /api/connectors/{id}/test`  
  - `csv-upload`:
    - Uses `/api/health` as a readiness check
    - Returns `{ connector, ok, message }`
  - others: placeholder response (“planned”)

### 4. Monitoring & Metrics

**Activity tracking**

Every meaningful backend operation calls `_record_activity(kind, status)`:

- `kind`: `"analyze"`, `"upload"`, `"inspect-schema"`, `"connector-test"`
- `status`: HTTP status code

This does two things:

1. Updates **in-memory counters** for fast dashboard metrics
2. Persists activity event to MongoDB (`activity_logs` collection) via `_record_activity_db(...)`

**APIs:**

- `GET /api/metrics`
  - exposes in-memory counters:
    - `total_analyze_requests`
    - `total_file_uploads`
    - `total_errors`
    - `last_request_at`
    - `activity_count`
- `GET /api/activity?limit=50`
  - reads from MongoDB (`activity_logs`), sorted by `timestamp` desc
  - falls back to in-memory ring buffer if DB is unavailable
  - response shape:
    ```json
    {
      "items": [
        {
          "id": "uuid",
          "kind": "analyze",
          "status": 200,
          "timestamp": "2025-08-20T12:34:56Z"
        }
      ]
    }
    ```

---

## 🧱 Architecture Overview

```text
React Frontend
   ↓ (via REACT_APP_BACKEND_URL + /api prefix)
FastAPI Backend (server.py)
   ↓
MongoDB (activity_logs collection for monitoring)
```

- All backend routes are **prefixed with `/api`** for Kubernetes ingress compatibility.
- **No hardcoded URLs**:
  - Frontend uses `REACT_APP_BACKEND_URL`
  - Backend uses `MONGO_URL` and `DB_NAME` from `backend/.env`

Key backend components:

- `server.py` – main FastAPI app, routes, CORS, metrics, activity logging
- `agent_core.py` – DataAnalystAgent & Gemini integration (optional)
- `requirements.txt` – Python dependencies

Key frontend components:

- `src/App.js` – main UI (tabs: Overview, Workspace, Connectors)
- `src/App.css` – styling (Tailwind + custom)
- `frontend/.env` – contains `REACT_APP_BACKEND_URL`

---

## ⚙️ Running & Managing Services

> All commands assume you’re inside the container at `/app`.

### Supervisor Control

```bash
# Restart backend only
cd /app
sudo supervisorctl restart backend

# Restart frontend only
cd /app
sudo supervisorctl restart frontend

# Restart all services (backend, frontend, mongodb, proxy, etc.)
cd /app
sudo supervisorctl restart all

# Check status of all services
cd /app
sudo supervisorctl status
```

---

## 🔍 Backend: Health & API Testing

Run these from inside the container.

### Health

```bash
curl -sS http://localhost:8001/api/health
# -> {"status":"healthy","message":"Data Analyst Agent is running"}
```

### Metrics

```bash
curl -sS http://localhost:8001/api/metrics
# -> {"total_analyze_requests": ..., "total_file_uploads": ..., ...}
```

### Activity (MongoDB-backed)

```bash
curl -sS 'http://localhost:8001/api/activity?limit=50'
# -> {"items":[...]}
```

### Analyze Endpoint (JSON)

```bash
curl -sS http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize your analysis capabilities", "context": {}}'
```

### File Upload Analysis

```bash
cd /app
curl -sS -X POST http://localhost:8001/api/ \
  -F 'questions.txt=Analyze this dataset and summarize key insights.' \
  -F 'data.csv=@sample.csv'
```

### Schema Inspection

```bash
cd /app
curl -sS -X POST http://localhost:8001/api/inspect-schema \
  -F "file=@sample.csv"
```

### Connectors

```bash
# List connectors
curl -sS http://localhost:8001/api/connectors

# Test CSV upload connector
curl -sS -X POST http://localhost:8001/api/connectors/csv-upload/test
```

---

## 🗄 MongoDB Persistence Details

The backend uses `motor.motor_asyncio.AsyncIOMotorClient` and the existing `MONGO_URL` / `DB_NAME` from `backend/.env`.

**Collection used:**

- `activity_logs` in database `DB_NAME`

Document shape:

```json
{
  "_id": "uuid-string",
  "kind": "analyze",
  "status": 200,
  "timestamp": "2025-08-20T12:34:56Z",
  "metadata": {}
}
```

Persistence is **best-effort**:
- If MongoDB is temporarily unavailable:
  - Errors are logged
  - Requests still succeed (activity persistence never breaks user flows)
  - `/api/activity` falls back to in-memory events

---

## 🖥 Frontend Usage

Once services are running:

1. Open the frontend URL (configured in `frontend/.env` as `REACT_APP_BACKEND_URL` for backend; the frontend itself runs on port 3000 internally and is exposed via the platform).
2. You’ll see **“Data Bridge Platform”** with three tabs:
   - **Overview** – metrics + recent activity
   - **Workspace** – question input, file upload, schema preview, responses
   - **Connectors** – connector list + CSV connector test

The UI is fully instrumented with `data-testid` attributes for automated testing of:

- Buttons / tabs
- Textareas / inputs
- Toasts
- Metrics cards
- Activity rows
- Connectors list

---

## 🧪 Basic Sanity Check Sequence

```bash
cd /app
sudo supervisorctl restart all
sleep 5

curl -sS http://localhost:8001/api/health
curl -sS http://localhost:8001/api/metrics
curl -sS 'http://localhost:8001/api/activity?limit=10'
```

Then:

- Open the frontend
- Ask a question
- Upload a CSV
- Check:
  - Overview tab metrics increase
  - Activity list shows events
  - Connectors tab “CSV File Upload → Test connector” shows success

---

## 🐛 Logs & Debugging

If something misbehaves:

```bash
# Backend error log
tail -n 100 /var/log/supervisor/backend.err.log

# Backend stdout log
tail -n 100 /var/log/supervisor/backend.out.log

# Frontend logs (if needed)
tail -n 100 /var/log/supervisor/frontend.err.log
tail -n 100 /var/log/supervisor/frontend.out.log
```

Use these together with browser DevTools (Console + Network) to diagnose issues like failed requests, 500s, or CORS errors.

---

## 🔮 Next Steps / Extensions

This foundation supports:

- Adding **transformation rules** on top of schema inspection
- Persisting **pipeline definitions** and workflows in MongoDB
- Introducing **authentication** (JWT / OAuth) for multi-user dashboards
- Enriching metrics with time-window aggregations (daily/weekly)

For now, you have a solid MVP with:

- End-to-end integration
- Persistent activity logs
- A dashboard, workspace, and connectors panel
- Health checks and testable endpoints
```

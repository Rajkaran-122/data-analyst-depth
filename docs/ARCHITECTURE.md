# Architecture & Implementation

**Live Portal:** [https://data-analyst-depth.vercel.app/](https://data-analyst-depth.vercel.app/)

This document covers the core architecture, data pipelines, and relationship databases utilized inside Data Analyst Depth (DAD).

## 1. System Context Architecture
The platform is built on an isolated, containerable micro-architecture with the frontend decoupled natively from the FastAPI engine, communicating exclusively over pure JSON and Multipart arrays.

```mermaid
graph TD
    Client[React Client UI]
    LoadBalancer[Gateway / Load Balancing]
    API_Layer[FastAPI Server Layer]
    AI_Agent[Data Analyst Agent Engine]
    LLM_API[Google Gemini / OpenAI]
    DataLake[(Physical Data Lake Cache ./data_lake)]
    Database[(SQLite Persistant Metadata .db)]

    Client --> |REST API HTTP Requests| LoadBalancer
    LoadBalancer --> API_Layer
    
    API_Layer <--> |Reads / Writes schemas| Database
    API_Layer <--> |Reads / Serializes bytes| DataLake
    
    API_Layer --> |Routes complex context queries| AI_Agent
    AI_Agent <--> |Dynamic Agent Reasoning| LLM_API
```

---

## 2. Data Flow Diagram (DFD)
Whenever a user uploads a file with a question via the Workspace UI, it triggers the analytical processing engine pipeline. Massive scale logic is dumped internally into background `asyncio` threadpools to decouple logic blocking.

```mermaid
sequenceDiagram
    participant User
    participant ChatInterface as Frontend Chat
    participant Routing as FastAPI Routes
    participant Storage as DB Storage DAO
    participant Core as DataAgent Core
    participant LLM as External LLM

    User->>ChatInterface: Select CSV & Ask "Find anomaly in revenue"
    ChatInterface->>Routing: POST multipart buffer (file) + JSON (key overrides)
    Routing->>Routing: Dump data to physical /data_lake
    Routing->>Storage: Store metadata context in DatasetMeta
    Routing->>Core: Invoke run_in_threadpool(agent.process_question)
    
    Core->>LLM: Pass environment secrets / system instructions
    LLM-->>Core: Returns Sandbox-tested JSON formatting
    Core->>Routing: Pass verified JSON structure
    Routing->>Storage: Log user ReportMetrics
    Routing-->>ChatInterface: Deliver AnalysisResponse schema
    ChatInterface-->>User: Visualizes responsive Rechart Graphs visually!
```

---

## 3. Database Schema (Entity Relationship Diagram - ERD)
We map all models natively using `SQLAlchemy`.

```mermaid
erDiagram
    DATASET {
        string id PK
        string user_id
        string name
        string filename
        int size_bytes
        int row_count
        int column_count
        json columns
        json preview
        string uploaded_at
        string status
    }
    
    REPORT {
        string id PK
        string title
        string dataset_id FK
        string query
        text summary
        json insights
        string created_at
        string status
    }

    QUERYLOG {
        string id PK
        text query
        string dataset_id FK
        int response_time_ms
        string status
        string timestamp
    }

    WORKSPACE {
        string id PK
        string name
        string description
        string color
        json dataset_ids "Array of dataset UUIDs"
        string created_at
        string updated_at
    }

    WORKSPACE ||--o{ DATASET : "contains"
    DATASET ||--o{ REPORT : "generates"
    DATASET ||--o{ QUERYLOG : "tracked by"
```

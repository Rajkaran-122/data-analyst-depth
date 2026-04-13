# Business Requirements Document (BRD)
**Project Name:** Data Analyst Depth (DAD)  
**Live Portal:** [https://data-analyst-depth.vercel.app/](https://data-analyst-depth.vercel.app/)  
**Document Version:** 1.0  
**Date:** 2026-04-13  

---

## 1. Executive Summary
Data Analyst Depth (DAD) is a centralized web platform crafted to automate the exhaustive and repetitive tasks associated with data formatting, analysis, and visualization. Utilizing advanced Large Language Models (LLMs) via Google Gemini or OpenAI GPT-4o, the application ingests raw data arrays (`.csv`, `.xlsx`, `.json`), formulates analytical scripts through conversational prompts, and visualizes outcomes automatically utilizing a highly interactive frontend.

## 2. Problem Statement
Business operations and marketing teams consistently possess high volumes of raw quantitative data. However, they lack the Python and Pandas expertise required to actively clean, evaluate, and extract visualization components from this data. Traditional Business Intelligence tools (like Tableau or PowerBI) demand immense setup overhead and database networking knowledge.

DAD attempts to seamlessly bridge this gap. By utilizing a "Drop and Ask" design, users can upload raw files into the workspace and immediately ask conversational questions about their data. 

## 3. Scope & Objectives
### **In-Scope**
- Conversion and normalization of user-uploaded datasets.
- Fast, async background execution via server thread pools for avoiding UX blocking.
- A functional persistent file cache map (`Data Lake`).
- Relational mapping of user queries, reports, and workspaces to a persistent fast-access SQLite database.
- Dynamic key overriding natively inside the frontend for localized context.

### **Out-of-Scope (Future Iterations)**
- Real-time multiplayer collaboration.
- Enterprise SSO directory configurations.
- Direct live-socket pipeline ingest streams from AWS/GCP buckets.

## 4. Target Audience
1. **Financial Analysts:** Need to determine anomalous trends rapidly without managing massive excel macro scripts.
2. **Sales Managers:** Analyzing historical performance logs based on localized regional metadata.
3. **Internal Product Operations:** Monitoring support tickets or application logs.

## 5. Functional Requirements
* **FR1 - AI Routing:** The platform must determine whether to route analytical queries through local offline heuristic routers or to ping an LLM engine based on the availability of an API token.
* **FR2 - Data Sanitization:** Corrupted or localized formatting parameters (like Excel Timestamps) must gracefully strip to generic UTC parameters prior to processing.
* **FR3 - Async Processing:** Any task that requires execution complexity greater than `O(n)` (e.g. standard Pandas parsing models) MUST be passed to an asyncio threadpool executor to maintain frontend responsiveness.
* **FR4 - Dynamic Authentication:** Users must be able to securely input and leverage their own private LLM tokens entirely restricted to their local session context.

## 6. Non-Functional Requirements
* **Security:** API Keys injected via the front end MUST NOT persistently log inside backend debug streams. 
* **Reliability:** Data upload chunks should persist securely upon unexpected application shutdown (via `data_lake` standard persistence).
* **Speed:** The application should prioritize instantaneous JSON response schemas utilizing streaming components.

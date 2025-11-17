import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import "@/App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

function formatTimestamp(date) {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function App() {
  const [activeTab, setActiveTab] = useState("workspace");

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isInspectingSchema, setIsInspectingSchema] = useState(false);
  const [backendHealthy, setBackendHealthy] = useState(null);
  const [toast, setToast] = useState(null);
  const [uploadHover, setUploadHover] = useState(false);

  const [metrics, setMetrics] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loadingOverview, setLoadingOverview] = useState(false);

  const [connectors, setConnectors] = useState([]);
  const [loadingConnectors, setLoadingConnectors] = useState(false);
  const [testingConnectorId, setTestingConnectorId] = useState(null);

  const [schemaInfo, setSchemaInfo] = useState(null);

  const hasBackendUrl = useMemo(() => Boolean(BACKEND_URL), []);

  const showToast = useCallback((type, message) => {
    setToast({ type, message });
    const id = setTimeout(() => setToast(null), 3500);
    return () => clearTimeout(id);
  }, []);

  const appendMessage = useCallback((content, role) => {
    setMessages((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        role,
        content,
        createdAt: new Date(),
      },
    ]);
  }, []);

  const checkHealth = useCallback(async () => {
    if (!hasBackendUrl) return;
    try {
      const res = await fetch(`${API_BASE}/health`, { method: "GET" });
      const ok = res.ok;
      setBackendHealthy(ok);
    } catch (e) {
      setBackendHealthy(false);
    }
  }, [hasBackendUrl]);

  const fetchOverview = useCallback(async () => {
    if (!hasBackendUrl) return;
    setLoadingOverview(true);
    try {
      const [metricsRes, activityRes] = await Promise.all([
        fetch(`${API_BASE}/metrics`),
        fetch(`${API_BASE}/activity`),
      ]);

      if (metricsRes.ok) {
        const m = await metricsRes.json();
        setMetrics(m);
      }

      if (activityRes.ok) {
        const a = await activityRes.json();
        setActivity(Array.isArray(a.items) ? a.items : []);
      }
    } catch (e) {
      showToast("error", "Failed to load overview data.");
    } finally {
      setLoadingOverview(false);
    }
  }, [hasBackendUrl, showToast]);

  const fetchConnectors = useCallback(async () => {
    if (!hasBackendUrl) return;
    setLoadingConnectors(true);
    try {
      const res = await fetch(`${API_BASE}/connectors`);
      if (res.ok) {
        const list = await res.json();
        setConnectors(Array.isArray(list) ? list : []);
      }
    } catch (e) {
      showToast("error", "Failed to load connectors.");
    } finally {
      setLoadingConnectors(false);
    }
  }, [hasBackendUrl, showToast]);

  useEffect(() => {
    if (!hasBackendUrl) return;
    checkHealth();
    const id = setInterval(checkHealth, 30000);
    return () => clearInterval(id);
  }, [checkHealth, hasBackendUrl]);

  useEffect(() => {
    if (!hasBackendUrl) return;
    if (activeTab === "overview") {
      fetchOverview();
    } else if (activeTab === "connectors") {
      fetchConnectors();
    }
  }, [activeTab, fetchConnectors, fetchOverview, hasBackendUrl]);

  const handleAsk = async () => {
    const trimmed = question.trim();
    if (!trimmed || !hasBackendUrl || isSending) return;

    appendMessage(trimmed, "user");
    setIsSending(true);

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed, context: {} }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = await res.json();
      let reply = "";
      if (data.explanation) {
        reply = data.explanation;
      } else if (data.result) {
        reply =
          typeof data.result === "string" ? data.result : JSON.stringify(data.result, null, 2);
      } else {
        reply = JSON.stringify(data, null, 2);
      }

      appendMessage(reply, "assistant");
      showToast("success", "Analysis completed.");
    } catch (e) {
      appendMessage(`Error from backend: ${e.message}`, "assistant");
      showToast("error", "Failed to analyze question.");
    } finally {
      setIsSending(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setSchemaInfo(null);
  };

  const handleUpload = async () => {
    if (!selectedFile || !hasBackendUrl || isUploading) return;

    setIsUploading(true);

    // Create a virtual questions.txt file from the current question (or a default prompt)
    const qText = question.trim() || "Analyze this dataset and summarize key insights.";
    const questionBlob = new Blob([qText], { type: "text/plain" });
    const questionFile = new File([questionBlob], "questions.txt", { type: "text/plain" });

    const formData = new FormData();
    formData.append("questions.txt", questionFile);
    formData.append("data.csv", selectedFile);

    try {
      const res = await fetch(`${API_BASE}/`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const pretty = typeof data === "string" ? data : JSON.stringify(data, null, 2);

      appendMessage(`File: ${selectedFile.name}\n\n${pretty}`, "assistant");
      showToast("success", "File uploaded and analyzed.");
    } catch (e) {
      appendMessage(`Error processing file: ${e.message}`, "assistant");
      showToast("error", "File upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleInspectSchema = async () => {
    if (!selectedFile || !hasBackendUrl || isInspectingSchema) return;

    setIsInspectingSchema(true);
    setSchemaInfo(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch(`${API_BASE}/inspect-schema`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setSchemaInfo(data);
      showToast("success", "Schema inspected successfully.");
    } catch (e) {
      showToast("error", "Schema inspection failed.");
    } finally {
      setIsInspectingSchema(false);
    }
  };

  const handleQuickPrompt = (prompt) => {
    setQuestion(prompt);
  };

  const handleTestConnector = async (id) => {
    if (!hasBackendUrl || testingConnectorId) return;
    setTestingConnectorId(id);
    try {
      const res = await fetch(`${API_BASE}/connectors/${id}/test`, {
        method: "POST",
      });
      let data = null;
      try {
        data = await res.json();
      } catch (e) {
        // ignore
      }
      if (res.ok) {
        showToast("success", data?.message || "Connector test successful.");
      } else {
        showToast("error", data?.error || "Connector test failed.");
      }
    } catch (e) {
      showToast("error", "Connector test failed.");
    } finally {
      setTestingConnectorId(null);
    }
  };

  const statusLabel = useMemo(() => {
    if (!hasBackendUrl) return "Backend URL missing";
    if (backendHealthy == null) return "Checking backend";
    return backendHealthy ? "Connected" : "Disconnected";
  }, [backendHealthy, hasBackendUrl]);

  return (
    <div className="App">
      <main className="app-shell" data-testid="data-analyst-app-shell">
        <section className="card-glass" data-testid="data-analyst-main-card">
          {/* Header */}
          <div className="card-section px-5 py-4 flex items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="badge" data-testid="connection-badge">
                <span className="badge-dot" />
                <span className="font-medium">Data Bridge</span>
              </div>
              <h1 className="text-lg sm:text-xl font-semibold">Data Bridge Platform</h1>
              <p className="text-xs sm:text-sm text-gray-400 max-w-xl">
                Connect data sources, inspect schemas, and send questions to the analytics agent from a
                single workspace.
              </p>
            </div>
            <div className="flex flex-col items-end gap-1 text-xs" data-testid="backend-status">
              <div className="flex items-center gap-2">
                <span
                  className={`status-dot ${
                    backendHealthy ? "connected" : backendHealthy === false ? "disconnected" : ""
                  }`}
                />
                <span>{statusLabel}</span>
              </div>
              <button
                type="button"
                className="button-outline"
                onClick={checkHealth}
                data-testid="backend-health-refresh-button"
              >
                Refresh
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="card-section px-5 pt-3 pb-2 flex flex-wrap gap-2 text-xs">
            <button
              type="button"
              className={`button-outline ${activeTab === "overview" ? "badge-pill" : ""}`}
              onClick={() => setActiveTab("overview")}
              data-testid="tab-overview"
            >
              Overview
            </button>
            <button
              type="button"
              className={`button-outline ${activeTab === "workspace" ? "badge-pill" : ""}`}
              onClick={() => setActiveTab("workspace")}
              data-testid="tab-workspace"
            >
              Workspace
            </button>
            <button
              type="button"
              className={`button-outline ${activeTab === "connectors" ? "badge-pill" : ""}`}
              onClick={() => setActiveTab("connectors")}
              data-testid="tab-connectors"
            >
              Connectors
            </button>
          </div>

          {/* Body: conditional per tab */}
          {activeTab === "workspace" && (
            <div className="card-section px-5 py-4 grid md:grid-cols-5 gap-4">
              {/* Left: input + upload */}
              <div className="md:col-span-3 space-y-4">
                {/* Question input */}
                <div className="input-shell">
                  <label className="input-label" htmlFor="question-input">
                    Question
                  </label>
                  <textarea
                    id="question-input"
                    data-testid="question-textarea"
                    className="textarea"
                    placeholder="Example: Explain monthly revenue trends and highlight anomalies"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                  />
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-2 text-[0.7rem] text-gray-400">
                      <span className="badge-pill" data-testid="backend-url-pill">
                        {hasBackendUrl ? "Using configured backend URL" : "REACT_APP_BACKEND_URL not set"}
                      </span>
                      <span className="badge-pill">JSON over HTTP</span>
                    </div>
                    <button
                      type="button"
                      className="button-primary"
                      onClick={handleAsk}
                      disabled={!hasBackendUrl || isSending || !question.trim()}
                      data-testid="ask-question-button"
                    >
                      {isSending ? "Analyzing..." : "Ask AI"}
                    </button>
                  </div>
                </div>

                {/* File upload */}
                <div className="space-y-2">
                  <label className="input-label">Dataset</label>
                  <div
                    className={`upload-dropzone ${uploadHover ? "hovered" : ""}`}
                    data-testid="file-upload-dropzone"
                    onDragEnter={() => setUploadHover(true)}
                    onDragLeave={() => setUploadHover(false)}
                    onDragOver={(e) => {
                      e.preventDefault();
                      setUploadHover(true);
                    }}
                    onDrop={(e) => {
                      e.preventDefault();
                      setUploadHover(false);
                      const file = e.dataTransfer.files?.[0];
                      if (file) {
                        setSelectedFile(file);
                        setSchemaInfo(null);
                      }
                    }}
                  >
                    <input
                      type="file"
                      accept=".csv,.xlsx,.xls,.json"
                      className="upload-input"
                      onChange={handleFileChange}
                      data-testid="file-input"
                    />
                    <div className="flex items-center justify-between gap-3">
                      <div className="space-y-1 text-xs">
                        <div className="flex items-center gap-2">
                          <span className="chip">Drop CSV / XLSX / JSON</span>
                        </div>
                        <p className="text-gray-400">
                          We automatically create a questions.txt payload and send everything to <code>/api/</code>.
                        </p>
                      </div>
                      {selectedFile && (
                        <div className="text-right text-xs" data-testid="selected-file-summary">
                          <div className="font-medium">{selectedFile.name}</div>
                          <div className="text-gray-400">{(selectedFile.size / 1024).toFixed(1)} KB</div>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-wrap justify-end gap-2">
                    <button
                      type="button"
                      className="button-outline"
                      onClick={handleInspectSchema}
                      disabled={!selectedFile || !hasBackendUrl || isInspectingSchema}
                      data-testid="inspect-schema-button"
                    >
                      {isInspectingSchema ? "Inspecting..." : "Inspect schema"}
                    </button>
                    <button
                      type="button"
                      className="button-outline"
                      onClick={handleUpload}
                      disabled={!selectedFile || !hasBackendUrl || isUploading}
                      data-testid="upload-analyze-button"
                    >
                      {isUploading ? "Uploading..." : "Upload & Analyze"}
                    </button>
                  </div>

                  {schemaInfo && (
                    <div className="space-y-2" data-testid="schema-preview">
                      <div className="flex items-center justify-between">
                        <span className="input-label">Schema preview</span>
                        <span className="badge-pill text-[0.65rem]">
                          {schemaInfo.row_count} rows · {schemaInfo.columns.length} columns
                        </span>
                      </div>
                      <div className="message-list" style={{ maxHeight: 200 }}>
                        <table className="w-full text-[0.7rem] text-left">
                          <thead>
                            <tr>
                              {schemaInfo.columns.map((c) => (
                                <th key={c.name} className="pr-3 pb-1 text-gray-400">
                                  {c.name}
                                  <span className="block text-[0.6rem] text-gray-500">{c.dtype}</span>
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {schemaInfo.preview.slice(0, 5).map((row, idx) => (
                              <tr key={idx}>
                                {schemaInfo.columns.map((c) => (
                                  <td key={c.name} className="pr-3 py-1 text-gray-200">
                                    {String(row[c.name])}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Right: quick prompts & meta */}
              <aside className="md:col-span-2 flex flex-col gap-4 text-xs">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="input-label">Quick prompts</span>
                  </div>
                  <div className="flex flex-wrap gap-2" data-testid="quick-prompts">
                    {[
                      "Summarize key trends in this dataset",
                      "Find anomalies or outliers in my data",
                      "Explain correlations between variables",
                      "Create a plain-language executive summary",
                    ].map((p) => (
                      <button
                        key={p}
                        type="button"
                        className="chip"
                        onClick={() => handleQuickPrompt(p)}
                        data-testid="quick-prompt-chip"
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="input-label">Latest responses</span>
                  <div className="message-list" data-testid="message-list">
                    {messages.length === 0 && (
                      <p className="text-gray-500 text-xs">
                        No messages yet. Ask a question or upload a file to get started.
                      </p>
                    )}
                    {messages.map((m) => (
                      <div
                        key={m.id}
                        className={`message-row ${m.role === "user" ? "user" : ""}`}
                        data-testid={m.role === "user" ? "message-user" : "message-assistant"}
                      >
                        <div className={`message-bubble ${m.role === "user" ? "user" : "bot"}`}>
                          <div>{m.content}</div>
                          <div className="message-meta">{formatTimestamp(m.createdAt)}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </aside>
            </div>
          )}

          {activeTab === "overview" && (
            <div className="card-section px-5 py-4 space-y-4" data-testid="overview-panel">
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                <div className="message-bubble bot" data-testid="metrics-card-analyze">
                  <div className="font-semibold text-gray-200 mb-1">Total questions</div>
                  <div className="text-2xl font-bold">
                    {metrics?.total_analyze_requests ?? "–"}
                  </div>
                </div>
                <div className="message-bubble bot" data-testid="metrics-card-uploads">
                  <div className="font-semibold text-gray-200 mb-1">Total file uploads</div>
                  <div className="text-2xl font-bold">
                    {metrics?.total_file_uploads ?? "–"}
                  </div>
                </div>
                <div className="message-bubble bot" data-testid="metrics-card-errors">
                  <div className="font-semibold text-gray-200 mb-1">Errors</div>
                  <div className="text-2xl font-bold text-red-400">
                    {metrics?.total_errors ?? "–"}
                  </div>
                </div>
                <div className="message-bubble bot" data-testid="metrics-card-last-request">
                  <div className="font-semibold text-gray-200 mb-1">Last activity</div>
                  <div className="text-xs text-gray-300">
                    {metrics?.last_request_at || "No activity yet"}
                  </div>
                </div>
              </div>

              <div className="space-y-2" data-testid="activity-list">
                <div className="flex items-center justify-between">
                  <span className="input-label">Recent activity</span>
                  {loadingOverview && <span className="text-[0.7rem] text-gray-400">Loading…</span>}
                </div>
                <div className="message-list" style={{ maxHeight: 220 }}>
                  {activity.length === 0 && (
                    <p className="text-xs text-gray-500">No activity recorded yet.</p>
                  )}
                  {activity.map((item) => (
                    <div
                      key={item.id}
                      className="message-row"
                      data-testid="activity-row"
                    >
                      <div className="message-bubble bot">
                        <div className="flex items-center justify-between gap-3">
                          <span className="badge-pill">{item.kind}</span>
                          <span className="text-[0.65rem] text-gray-400">{item.timestamp}</span>
                        </div>
                        <div className="message-meta">HTTP {item.status}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "connectors" && (
            <div className="card-section px-5 py-4 space-y-4" data-testid="connectors-panel">
              <div className="flex items-center justify-between">
                <span className="input-label">Data connectors</span>
                {loadingConnectors && (
                  <span className="text-[0.7rem] text-gray-400">Loading…</span>
                )}
              </div>
              <div className="message-list" data-testid="connectors-list">
                {connectors.length === 0 && (
                  <p className="text-xs text-gray-500">No connectors found.</p>
                )}
                {connectors.map((c) => (
                  <div
                    key={c.id}
                    className="message-row"
                    data-testid="connector-row"
                  >
                    <div className="message-bubble bot w-full flex flex-col gap-1">
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                          <span className="font-semibold text-gray-100">{c.name}</span>
                          <span className="text-[0.7rem] text-gray-400">Type: {c.type}</span>
                        </div>
                        <span className="badge-pill text-[0.65rem]">
                          {c.status === "active" ? "Active" : "Planned"}
                        </span>
                      </div>
                      {c.description && (
                        <p className="text-[0.75rem] text-gray-300">{c.description}</p>
                      )}
                      <div className="flex justify-end mt-1">
                        <button
                          type="button"
                          className="button-outline"
                          onClick={() => handleTestConnector(c.id)}
                          disabled={testingConnectorId === c.id || c.status !== "active"}
                          data-testid="connector-test-button"
                        >
                          {testingConnectorId === c.id
                            ? "Testing…"
                            : c.status === "active"
                              ? "Test connector"
                              : "Not available"}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {toast && (
          <div
            className={`toast ${
              toast.type === "success"
                ? "toast-success"
                : toast.type === "error"
                  ? "toast-error"
                  : "toast-info"
            }`}
            data-testid="toast"
          >
            <span className="toast-icon" aria-hidden="true">
              {toast.type === "success" && "✔"}
              {toast.type === "error" && "⚠"}
              {toast.type === "info" && "ℹ"}
            </span>
            <div>{toast.message}</div>
            <button
              type="button"
              className="toast-close"
              onClick={() => setToast(null)}
              data-testid="toast-close-button"
            >
              ×
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

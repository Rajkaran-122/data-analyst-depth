/**
 * DataFlow - Professional Analytics AI Agent Frontend
 * v2.0 - Tailwind CSS Edition with Enhanced Features
 */

// Configuration
const API_URL = 'https://web-production-0249c.up.railway.app';
const STORAGE_KEY = 'dataflow-session-v2';
const HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
const RECONNECT_INTERVAL = 5000; // 5 seconds

// API Endpoints (matching backend routes)
const ENDPOINTS = {
    HEALTH: `${API_URL}/health`,
    ANALYZE: `${API_URL}/analyze`,
    UPLOAD: `${API_URL}/api/`,
    ROOT: `${API_URL}/`
};

// State management
const state = {
    conversationHistory: [],
    uploadedFiles: [],
    recentQueries: [],
    isConnected: false,
    isSending: false,
    healthCheckTimer: null,
    reconnectTimer: null,
    messageCount: 0,
    fileCount: 0
};

// DOM Elements
const elements = {
    sidebar: document.getElementById('sidebar'),
    sidebarToggle: document.getElementById('sidebarToggle'),
    sidebarClose: document.getElementById('sidebarClose'),
    sidebarOverlay: document.getElementById('sidebarOverlay'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    messagesArea: document.getElementById('messagesArea'),
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    toast: document.getElementById('toast'),
    toastIcon: document.getElementById('toastIcon'),
    toastMessage: document.getElementById('toastMessage'),
    resultModal: document.getElementById('resultModal'),
    modalContent: document.getElementById('modalContent'),
    closeModal: document.getElementById('closeModal'),
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    recentQueriesList: document.getElementById('recentQueriesList'),
    statsFiles: document.getElementById('statsFiles'),
    statsQueries: document.getElementById('statsQueries'),
    quickActions: document.querySelectorAll('.quick-action-btn'),
    loadingIndicator: document.getElementById('loadingIndicator')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadStoredData();
    checkBackendStatus();
    startHealthCheck();
    updateStats();
});

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Sidebar toggle
    if (elements.sidebarToggle) {
        elements.sidebarToggle.addEventListener('click', openSidebar);
    }
    
    // Sidebar close button (mobile)
    if (elements.sidebarClose) {
        elements.sidebarClose.addEventListener('click', closeSidebar);
    }
    
    // Sidebar overlay (mobile)
    if (elements.sidebarOverlay) {
        elements.sidebarOverlay.addEventListener('click', closeSidebar);
    }
    
    // Close sidebar on nav item click (mobile)
    if (window.innerWidth < 768) {
        document.querySelectorAll('#sidebar .nav-item').forEach(item => {
            item.addEventListener('click', closeSidebar);
        });
    }

    // Message input
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send button
    elements.sendBtn.addEventListener('click', sendMessage);

    // File upload
    elements.uploadArea.addEventListener('click', () => elements.fileInput.click());
    elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.add('border-accent');
    });
    elements.uploadArea.addEventListener('dragleave', () => {
        elements.uploadArea.classList.remove('border-accent');
    });
    elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.remove('border-accent');
        processFiles(e.dataTransfer.files);
    });

    elements.fileInput.addEventListener('change', (e) => {
        processFiles(e.target.files);
    });

    // Modal close
    elements.closeModal.addEventListener('click', closeModal);
    elements.resultModal.addEventListener('click', (e) => {
        if (e.target === elements.resultModal) closeModal();
    });

    // Quick action buttons
    elements.quickActions.forEach((btn, index) => {
        btn.addEventListener('click', () => quickAnalysis(index));
    });

    // Toast close
    document.querySelector('#toast button').addEventListener('click', () => {
        elements.toast.classList.add('hidden');
    });
}

/**
 * Open sidebar (mobile)
 */
function openSidebar() {
    if (!elements.sidebar) return;
    elements.sidebar.classList.add('sidebar-open');
    elements.sidebar.classList.remove('-translate-x-full', 'sidebar-close');
    
    // Show overlay
    if (elements.sidebarOverlay) {
        elements.sidebarOverlay.classList.remove('hidden');
        elements.sidebarOverlay.style.animation = 'fadeIn 0.3s ease-out';
    }
}

/**
 * Close sidebar (mobile)
 */
function closeSidebar() {
    if (!elements.sidebar) return;
    elements.sidebar.classList.add('sidebar-close', '-translate-x-full');
    elements.sidebar.classList.remove('sidebar-open');
    
    // Hide overlay
    if (elements.sidebarOverlay) {
        elements.sidebarOverlay.classList.add('hidden');
    }
}

/**
 * Send message to backend
 */
async function sendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message || state.isSending) return;

    state.isSending = true;
    elements.sendBtn.disabled = true;

    // Add user message to UI
    addMessage(message, true);
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';

    try {
        // Add thinking indicator
        const thinkingMsg = document.createElement('div');
        thinkingMsg.className = 'flex gap-3 message-bot';
        thinkingMsg.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0">
                <i class="fas fa-brain text-white text-sm"></i>
            </div>
            <div class="flex-1">
                <div class="inline-block bg-muted/50 rounded-lg px-4 py-2">
                    <div class="flex gap-1">
                        <div class="w-2 h-2 rounded-full bg-accent/50 animate-bounce"></div>
                        <div class="w-2 h-2 rounded-full bg-accent/50 animate-bounce" style="animation-delay: 0.1s"></div>
                        <div class="w-2 h-2 rounded-full bg-accent/50 animate-bounce" style="animation-delay: 0.2s"></div>
                    </div>
                </div>
            </div>
        `;
        elements.messagesArea.appendChild(thinkingMsg);
        scrollToBottom();

        console.log('📤 Sending to /analyze:', { question: message, context: {} });
        
        const response = await fetch(ENDPOINTS.ANALYZE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                question: message,
                context: {}
            })
        });

        console.log('📥 Response status:', response.status, response.statusText);
        
        if (!response.ok) {
            const contentType = response.headers.get('content-type');
            let errorDetails = '';
            
            if (contentType && contentType.includes('application/json')) {
                try {
                    const errorData = await response.json();
                    console.error('❌ Error response JSON:', errorData);
                    errorDetails = errorData.detail || errorData.message || JSON.stringify(errorData);
                } catch (e) {
                    errorDetails = 'Invalid error response format';
                }
            } else {
                errorDetails = await response.text();
            }
            
            throw new Error(`HTTP ${response.status}: ${errorDetails || response.statusText}`);
        }

        const data = await response.json();
        console.log('✅ Analysis response received:', data);
        thinkingMsg.remove();
        
        // Handle response - backend returns different fields
        let responseText = '';
        if (data.explanation) {
            responseText = data.explanation;
        } else if (data.result) {
            responseText = `Result: ${typeof data.result === 'string' ? data.result : JSON.stringify(data.result)}`;
        } else if (data.response) {
            responseText = data.response;
        } else {
            responseText = JSON.stringify(data);
        }
        
        addMessage(responseText, false);
        
        // Track query
        state.recentQueries.unshift(message);
        if (state.recentQueries.length > 10) state.recentQueries.pop();
        state.messageCount++;
        
        saveData();
        updateStats();
        showToast('Analysis complete!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        state.isSending = false;
        elements.sendBtn.disabled = false;
    }
}

/**
 * Process uploaded files
 */
async function processFiles(files) {
    if (!files.length) return;

    for (const file of files) {
        // Validate file
        const validExtensions = ['.csv', '.xlsx', '.xls', '.json'];
        const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        const maxSize = 50 * 1024 * 1024; // 50MB

        if (!validExtensions.includes(fileExtension)) {
            showToast(`❌ Invalid file type: ${file.name}. Supported: CSV, XLSX, JSON`, 'error');
            continue;
        }

        if (file.size > maxSize) {
            showToast(`❌ File too large: ${file.name} (${formatFileSize(file.size)})`, 'error');
            continue;
        }

        // Show upload starting message
        showToast(`📤 Uploading ${file.name}...`, 'info');
        console.log(`Starting upload: ${file.name} (${formatFileSize(file.size)})`);

        // Upload file
        try {
            const formData = new FormData();
            // Send the file with the key matching what backend expects
            // Backend looks for 'questions.txt' first, then 'question', then any file
            formData.append('questions.txt', file);

            console.log(`Sending to ${ENDPOINTS.UPLOAD}`);
            
            const response = await fetch(ENDPOINTS.UPLOAD, {
                method: 'POST',
                body: formData,
                // Don't set Content-Type header - browser will set it with boundary
                // This is important for multipart/form-data
            });

            console.log(`Upload response status: ${response.status}`);

            if (!response.ok) {
                const errorText = await response.text();
                console.error(`Upload error response: ${errorText}`);
                throw new Error(`Upload failed with status ${response.status}: ${errorText}`);
            }

            let data;
            try {
                data = await response.json();
                console.log('Upload response:', data);
            } catch (e) {
                console.error('Failed to parse response as JSON:', e);
                throw new Error('Invalid response format from server');
            }

            // Track file
            state.uploadedFiles.push({
                name: file.name,
                size: file.size,
                type: file.type,
                timestamp: Date.now()
            });
            state.fileCount++;

            // Show response from backend
            let responseMsg = '';
            let hasResult = false;

            if (data.explanation) {
                responseMsg = `📁 **File: ${file.name}**\n\n${data.explanation}`;
                hasResult = true;
            } else if (data.result && typeof data.result === 'object') {
                // Format object result nicely
                responseMsg = `📁 **File: ${file.name}**\n\n**Analysis Results:**\n\`\`\`json\n${JSON.stringify(data.result, null, 2)}\n\`\`\``;
                hasResult = true;
            } else if (data.result) {
                responseMsg = `📁 **File: ${file.name}** (${formatFileSize(file.size)})\n\n${data.result}`;
                hasResult = true;
            } else if (data.message) {
                responseMsg = `📁 **File: ${file.name}** (${formatFileSize(file.size)})\n\n${data.message}`;
                hasResult = true;
            } else if (data.status === 'success') {
                responseMsg = `✅ **File: ${file.name}** (${formatFileSize(file.size)}) uploaded and processed successfully!`;
                hasResult = true;
            } else if (Object.keys(data).length > 0) {
                // Display entire response as formatted JSON
                responseMsg = `📁 **File: ${file.name}** (${formatFileSize(file.size)})\n\n**Server Response:**\n\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\``;
                hasResult = true;
            } else {
                responseMsg = `✅ **File: ${file.name}** (${formatFileSize(file.size)}) uploaded successfully!`;
            }

            addMessage(responseMsg, false);
            saveData();
            updateStats();
            showToast(`✅ File processed: ${file.name}`, 'success');

        } catch (error) {
            console.error('Upload error:', error);
            console.error('Error stack:', error.stack);
            showToast(`❌ Upload failed: ${error.message}`, 'error');
            addMessage(`❌ **Error uploading ${file.name}**: ${error.message}`, false);
        }
    }

    // Reset file input
    elements.fileInput.value = '';
}

/**
 * Add message to chat
 */
function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    const messageClass = isUser 
        ? 'flex justify-end gap-3 message-user' 
        : 'flex gap-3 message-bot';
    
    messageDiv.className = messageClass;

    const contentDiv = document.createElement('div');
    
    if (isUser) {
        contentDiv.className = 'inline-block bg-gradient-to-r from-primary to-accent text-primary-foreground rounded-lg px-4 py-2 max-w-md lg:max-w-xl break-words';
        contentDiv.innerHTML = escapeHtml(content);
    } else {
        contentDiv.className = 'flex-1 flex gap-3';
        const avatar = document.createElement('div');
        avatar.className = 'w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0';
        avatar.innerHTML = '<i class="fas fa-robot text-white text-sm"></i>';
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'inline-block bg-muted/50 rounded-lg px-4 py-2 max-w-md lg:max-w-xl';
        bubbleDiv.innerHTML = formatMessage(content);
        
        contentDiv.appendChild(avatar);
        contentDiv.appendChild(bubbleDiv);
    }

    messageDiv.appendChild(contentDiv);
    elements.messagesArea.appendChild(messageDiv);
    
    // Track conversation
    state.conversationHistory.push({
        role: isUser ? 'user' : 'assistant',
        content: content,
        timestamp: Date.now()
    });

    scrollToBottom();
}

/**
 * Format message with markdown support
 */
function formatMessage(text) {
    // Escape HTML first
    let formatted = escapeHtml(text);
    
    // Bold
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.+?)__/g, '<strong>$1</strong>');
    
    // Italic
    formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/_(.+?)_/g, '<em>$1</em>');
    
    // Code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, (match, code) => {
        const highlighted = hljs.highlightAuto(code.trim()).value;
        return `<pre class="bg-background rounded px-3 py-2 overflow-x-auto"><code>${highlighted}</code></pre>`;
    });
    
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code class="bg-muted px-2 py-1 rounded text-sm">$1</code>');
    
    // Paragraphs
    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = `<p>${formatted}</p>`;
    
    return formatted;
}

/**
 * Quick analysis templates
 */
function quickAnalysis(index) {
    const templates = [
        'Generate a summary of this dataset',
        'Show me key statistics and distributions',
        'Create visualizations for this data',
        'What are the key insights and findings?'
    ];
    
    if (templates[index]) {
        elements.messageInput.value = templates[index];
        elements.messageInput.style.height = 'auto';
        elements.messageInput.focus();
    }
}

/**
 * Check backend health and all endpoints
 */
async function checkBackendStatus() {
    try {
        console.log('🔍 Checking backend connection...');
        
        // Test 1: Health endpoint
        let healthOk = false;
        try {
            const healthResponse = await fetch(ENDPOINTS.HEALTH, {
                method: 'GET',
                cache: 'no-cache',
                timeout: 5000
            });
            
            if (healthResponse.ok) {
                const healthData = await healthResponse.json();
                console.log('✅ Health check passed:', healthData);
                healthOk = healthData.status === 'healthy';
            }
        } catch (e) {
            console.warn('⚠️ Health endpoint error:', e.message);
        }
        
        // Test 2: Analyze endpoint (test with simple query)
        let analyzeOk = false;
        try {
            const analyzeResponse = await fetch(ENDPOINTS.ANALYZE, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: 'test', context: {} }),
                timeout: 5000
            });
            
            if (analyzeResponse.ok || analyzeResponse.status === 500) {
                console.log('✅ Analyze endpoint accessible (status: ' + analyzeResponse.status + ')');
                analyzeOk = true;
            }
        } catch (e) {
            console.warn('⚠️ Analyze endpoint error:', e.message);
        }
        
        // Test 3: API endpoint (test with empty multipart)
        let apiOk = false;
        try {
            const formData = new FormData();
            const apiResponse = await fetch(ENDPOINTS.UPLOAD, {
                method: 'POST',
                body: formData,
                timeout: 5000
            });
            
            // 400 is expected for empty upload, but shows endpoint works
            if (apiResponse.status === 400 || apiResponse.ok) {
                console.log('✅ API endpoint accessible (status: ' + apiResponse.status + ')');
                apiOk = true;
            }
        } catch (e) {
            console.warn('⚠️ API endpoint error:', e.message);
        }
        
        // Connection status
        if (healthOk && analyzeOk) {
            state.isConnected = true;
            elements.statusDot.classList.remove('bg-destructive', 'animate-pulse');
            elements.statusDot.classList.add('bg-green-500');
            elements.statusText.textContent = 'Connected';
            console.log('✅ Backend connection established');
            clearTimeout(state.reconnectTimer);
            return;
        }
        
        throw new Error('Backend connectivity check failed');
    } catch (error) {
        state.isConnected = false;
        elements.statusDot.classList.remove('bg-green-500');
        elements.statusDot.classList.add('bg-destructive', 'animate-pulse');
        elements.statusText.textContent = 'Disconnected';
        console.error('❌ Connection error:', error.message);
        
        // Retry connection
        if (!state.reconnectTimer) {
            state.reconnectTimer = setTimeout(checkBackendStatus, RECONNECT_INTERVAL);
            console.log('🔄 Retrying connection in ' + (RECONNECT_INTERVAL/1000) + 's...');
        }
    }
}

/**
 * Start periodic health checks
 */
function startHealthCheck() {
    if (state.healthCheckTimer) clearInterval(state.healthCheckTimer);
    state.healthCheckTimer = setInterval(checkBackendStatus, HEALTH_CHECK_INTERVAL);
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    elements.toastMessage.textContent = message;
    
    // Update icon based on type
    const icons = {
        success: 'fas fa-circle-check text-green-500',
        error: 'fas fa-circle-xmark text-destructive',
        info: 'fas fa-circle-info text-accent',
        warning: 'fas fa-circle-exclamation text-yellow-500'
    };
    
    elements.toastIcon.className = icons[type] || icons.info;
    elements.toast.classList.remove('hidden', 'animate-slide-in-right');
    void elements.toast.offsetWidth; // Trigger reflow
    elements.toast.classList.add('animate-slide-in-right');
    
    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, 4000);
}

/**
 * Open modal with results
 */
function openModal(content) {
    elements.modalContent.innerHTML = formatMessage(content);
    elements.resultModal.classList.remove('hidden');
    if (window.hljs) {
        elements.resultModal.querySelectorAll('code').forEach(el => {
            hljs.highlightElement(el);
        });
    }
}

/**
 * Close modal
 */
function closeModal() {
    elements.resultModal.classList.add('hidden');
}

/**
 * Scroll to bottom of messages
 */
function scrollToBottom() {
    setTimeout(() => {
        elements.messagesArea.scrollTop = elements.messagesArea.scrollHeight;
    }, 0);
}

/**
 * Save data to localStorage
 */
function saveData() {
    const data = {
        conversationHistory: state.conversationHistory,
        uploadedFiles: state.uploadedFiles,
        recentQueries: state.recentQueries,
        messageCount: state.messageCount,
        fileCount: state.fileCount
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

/**
 * Load data from localStorage
 */
function loadStoredData() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            const data = JSON.parse(stored);
            state.conversationHistory = data.conversationHistory || [];
            state.uploadedFiles = data.uploadedFiles || [];
            state.recentQueries = data.recentQueries || [];
            state.messageCount = data.messageCount || 0;
            state.fileCount = data.fileCount || 0;
            
            // Restore conversation
            state.conversationHistory.forEach(msg => {
                addMessage(msg.content, msg.role === 'user');
            });
        }
    } catch (error) {
        console.error('Failed to load stored data:', error);
    }
}

/**
 * Update statistics display
 */
function updateStats() {
    elements.statsFiles.textContent = state.fileCount;
    elements.statsQueries.textContent = state.messageCount;
    
    // Update recent queries
    if (state.recentQueries.length > 0) {
        elements.recentQueriesList.innerHTML = state.recentQueries
            .slice(0, 5)
            .map(q => `<p class="text-xs p-2 rounded bg-muted/30 truncate">${escapeHtml(q)}</p>`)
            .join('');
    }
}

/**
 * Utility: Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Utility: Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Auto-resize textarea
elements.messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (state.healthCheckTimer) clearInterval(state.healthCheckTimer);
    if (state.reconnectTimer) clearTimeout(state.reconnectTimer);
    saveData();
});

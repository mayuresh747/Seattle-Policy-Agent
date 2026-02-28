/* ═══════════════════════════════════════════════════════════════
   Chat Agent — Client Logic
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    // ── DOM refs ──────────────────────────────────────────────────
    const chatArea = document.getElementById('chatArea');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearChat = document.getElementById('clearChat');
    const openSettings = document.getElementById('openSettings');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const sidebarClose = document.getElementById('sidebarClose');
    const systemPrompt = document.getElementById('systemPrompt');
    const savePrompt = document.getElementById('savePrompt');
    const resetPrompt = document.getElementById('resetPrompt');
    const saveStatus = document.getElementById('saveStatus');
    const welcome = document.getElementById('welcome');
    const tempSlider = document.getElementById('tempSlider');
    const tempValue = document.getElementById('tempValue');

    // Dynamic UI elements
    const appTitle = document.getElementById('appTitle');
    const appSubtitle = document.getElementById('appSubtitle');
    const welcomeTitle = document.getElementById('welcomeTitle');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const exampleQueries = document.getElementById('exampleQueries');
    const inputHint = document.getElementById('inputHint');

    let isStreaming = false;
    let defaultPrompt = '';
    let sessionId = localStorage.getItem('chat_session_id');

    // Generate Session ID if missing
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        localStorage.setItem('chat_session_id', sessionId);
    }

    // ── Init ──────────────────────────────────────────────────────
    loadUIConfig();
    loadSettings();

    // ── Load UI config from server (from agent_config.yaml) ──────
    async function loadUIConfig() {
        try {
            const res = await fetch('/api/config');
            const data = await res.json();

            // Update header
            if (data.title) {
                appTitle.textContent = data.title;
                document.title = data.title;
                welcomeTitle.textContent = data.title;
            }
            if (data.subtitle) {
                appSubtitle.textContent = data.subtitle;
            }
            if (data.welcome_message) {
                welcomeMessage.textContent = data.welcome_message;
            }

            // Update input hint
            inputHint.textContent = `Powered by OpenAI`;

            // Render example queries
            if (data.example_queries && data.example_queries.length > 0) {
                renderExampleQueries(data.example_queries);
            }
        } catch (e) {
            console.error('Failed to load UI config:', e);
        }
    }

    function renderExampleQueries(queries) {
        exampleQueries.innerHTML = '';
        // Shuffle and pick up to 4
        const shuffled = [...queries].sort(() => 0.5 - Math.random());
        const selected = shuffled.slice(0, 4);

        selected.forEach(q => {
            const btn = document.createElement('button');
            btn.className = 'example-query';
            btn.textContent = q;
            btn.addEventListener('click', () => {
                chatInput.value = q;
                sendBtn.disabled = false;
                autoResize(chatInput);
                sendMessage();
            });
            exampleQueries.appendChild(btn);
        });
    }

    // ── Input handling ────────────────────────────────────────────
    chatInput.addEventListener('input', () => {
        sendBtn.disabled = !chatInput.value.trim() || isStreaming;
        autoResize(chatInput);
    });

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    // ── Clear chat ────────────────────────────────────────────────
    clearChat.addEventListener('click', async () => {
        try {
            await fetch(`/api/chat/history?session_id=${sessionId}`, {
                method: 'DELETE',
            });
            chatArea.innerHTML = '';
            chatArea.appendChild(welcome);
            welcome.style.display = 'flex';
            // Re-render random examples
            loadUIConfig();
        } catch (e) {
            console.error('Clear chat failed', e);
        }
    });

    // ── Sidebar ───────────────────────────────────────────────────
    openSettings.addEventListener('click', () => toggleSidebar(true));
    sidebarClose.addEventListener('click', () => toggleSidebar(false));
    sidebarOverlay.addEventListener('click', () => toggleSidebar(false));

    savePrompt.addEventListener('click', saveSettings);
    resetPrompt.addEventListener('click', () => {
        systemPrompt.value = defaultPrompt;
        tempSlider.value = 0.7;
        tempValue.textContent = '0.70';
        showSaveStatus('Reset to default — click Save to apply', '');
    });

    tempSlider.addEventListener('input', () => {
        tempValue.textContent = parseFloat(tempSlider.value).toFixed(2);
    });

    // ── Send message ──────────────────────────────────────────────
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || isStreaming) return;

        isStreaming = true;
        sendBtn.disabled = true;
        chatInput.value = '';
        autoResize(chatInput);

        // Hide welcome
        if (welcome) welcome.style.display = 'none';

        // Add user message
        addMessage('user', text);

        // Add assistant placeholder with thinking
        const assistantMsg = addMessage('assistant', '', true);
        const bubble = assistantMsg.querySelector('.message-bubble');

        // Show thinking indicator
        const startTime = Date.now();
        bubble.innerHTML = thinkingHTML();
        const thinkingTimer = setInterval(() => {
            const el = bubble.querySelector('.thinking-elapsed');
            if (el) {
                const secs = Math.floor((Date.now() - startTime) / 1000);
                el.textContent = `${secs}s`;
            }
        }, 1000);

        // Stream response
        let fullText = '';
        let usageData = null;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    session_id: sessionId,
                }),
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    try {
                        const event = JSON.parse(line.slice(6));
                        if (event.type === 'token') {
                            fullText += event.data;
                        } else if (event.type === 'usage') {
                            usageData = event.data;
                        } else if (event.type === 'error') {
                            clearInterval(thinkingTimer);
                            bubble.innerHTML = `<span style="color: var(--error);">${event.data}</span>`;
                        }
                    } catch (e) {
                        // skip malformed
                    }
                }
            }

            // Reveal final markdown
            clearInterval(thinkingTimer);
            bubble.classList.add('reveal');
            bubble.innerHTML = renderMarkdown(fullText);

            // Show token usage
            if (usageData) {
                const usageEl = document.createElement('div');
                usageEl.className = 'token-usage';
                const total = (usageData.input_tokens || 0) + (usageData.output_tokens || 0);
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                usageEl.textContent = `${total.toLocaleString()} tokens (${usageData.input_tokens.toLocaleString()} in · ${usageData.output_tokens.toLocaleString()} out) · ${elapsed}s`;
                bubble.parentElement.appendChild(usageEl);
            }

        } catch (err) {
            clearInterval(thinkingTimer);
            bubble.innerHTML = `<span style="color: var(--error);">Connection error: ${err.message || 'Unknown error'}</span>`;
        }

        isStreaming = false;
        sendBtn.disabled = !chatInput.value.trim();
        scrollToBottom();
    }

    // ── Add message to chat ───────────────────────────────────────
    function addMessage(role, content, showTyping = false) {
        const msg = document.createElement('div');
        msg.className = `message message-${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? 'U' : 'AI';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        if (showTyping) {
            bubble.innerHTML = typingHTML();
        } else {
            bubble.innerHTML = role === 'user' ? escapeHtml(content) : renderMarkdown(content);
        }

        contentDiv.appendChild(bubble);
        msg.appendChild(avatar);
        msg.appendChild(contentDiv);
        chatArea.appendChild(msg);
        scrollToBottom();

        return msg;
    }

    // ── Settings ──────────────────────────────────────────────────
    async function loadSettings() {
        try {
            const res = await fetch(`/api/settings?session_id=${sessionId}`);
            const data = await res.json();
            systemPrompt.value = data.system_prompt;
            defaultPrompt = data.system_prompt;
            if (data.temperature !== undefined) {
                tempSlider.value = data.temperature;
                tempValue.textContent = parseFloat(data.temperature).toFixed(2);
            }
        } catch (e) {
            console.error('Failed to load settings:', e);
        }
    }

    async function saveSettings() {
        try {
            const res = await fetch('/api/settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    system_prompt: systemPrompt.value,
                    temperature: parseFloat(tempSlider.value),
                }),
            });
            if (res.ok) {
                showSaveStatus('✓ Saved successfully', 'success');
            } else {
                showSaveStatus('Failed to save', 'error');
            }
        } catch (e) {
            showSaveStatus('Connection error', 'error');
        }
    }

    function showSaveStatus(text, className) {
        saveStatus.textContent = text;
        saveStatus.className = `save-status ${className}`;
        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = 'save-status';
        }, 3000);
    }

    function toggleSidebar(open) {
        sidebar.classList.toggle('open', open);
        sidebarOverlay.classList.toggle('open', open);
    }

    // ── Utilities ─────────────────────────────────────────────────
    function autoResize(el) {
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 150) + 'px';
    }

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function renderMarkdown(text) {
        if (!text) return '';
        try {
            const rawHtml = marked.parse(text, { breaks: true });
            return DOMPurify.sanitize(rawHtml);
        } catch (e) {
            return escapeHtml(text);
        }
    }

    function typingHTML() {
        return `<div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>`;
    }

    function thinkingHTML() {
        return `<div class="thinking-status">
            <div class="thinking-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <span class="thinking-label">Thinking…</span>
            <span class="thinking-elapsed">0s</span>
        </div>`;
    }
});

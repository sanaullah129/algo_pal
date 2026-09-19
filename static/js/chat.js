/* chat.js — algo_pal chat page */

const SESSION_ID = window.__SESSION_ID__;
let isLoading = false;

/* ============================================================
   Marked.js setup — custom renderer for code blocks
   ============================================================ */
const mdRenderer = {
  code(code, language) {
    const lang = (language || 'plaintext').trim();
    let highlighted;
    try {
      highlighted = (lang && hljs.getLanguage(lang))
        ? hljs.highlight(code, { language: lang }).value
        : hljs.highlightAuto(code).value;
    } catch {
      highlighted = escapeHtmlRaw(code);
    }
    const id = 'cb-' + Math.random().toString(36).slice(2);
    return `
      <div class="code-block-wrapper">
        <div class="code-block-header">
          <span class="code-lang">${escapeHtmlRaw(lang)}</span>
          <button class="btn-copy" onclick="copyCode('${id}',this)">Copy</button>
        </div>
        <pre><code id="${id}" class="hljs">${highlighted}</code></pre>
      </div>`;
  },
};
marked.use({ renderer: mdRenderer, breaks: true, gfm: true });

/* ============================================================
   Helpers
   ============================================================ */
function escapeHtmlRaw(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(text || ''));
  return d.innerHTML;
}

function renderMarkdown(text) {
  return marked.parse(text || '');
}

function copyCode(id, btn) {
  const el = document.getElementById(id);
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(() => {
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
  });
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  try {
    return new Date(dateStr).toLocaleString(undefined, {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  } catch { return ''; }
}

function showToast(msg) {
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

function scrollToBottom() {
  const el = document.getElementById('messages');
  el.scrollTop = el.scrollHeight;
}

/* ============================================================
   Message rendering
   ============================================================ */
function renderMessage(role, content, extra = {}) {
  const container = document.getElementById('messages');

  // Remove welcome screen on first real message
  const welcome = container.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  const wrap = document.createElement('div');
  wrap.className = `message ${role}`;

  const avatar = role === 'user' ? '👤' : '⚡';

  const bubble = role === 'user'
    ? `<div class="message-bubble">${escapeHtml(content).replace(/\n/g, '<br>')}</div>`
    : `<div class="message-bubble">${renderMarkdown(content)}</div>`;

  let extras = '';

  // Complexity card
  const c = extra.complexity;
  if (c && (c.time_complexity !== 'Not analyzed' || c.space_complexity !== 'Not analyzed')) {
    extras += `
      <div class="complexity-card">
        <div class="complexity-item">
          <span class="complexity-label">Time</span>
          <span class="complexity-value">${escapeHtml(c.time_complexity)}</span>
        </div>
        <div class="complexity-item">
          <span class="complexity-label">Space</span>
          <span class="complexity-value">${escapeHtml(c.space_complexity)}</span>
        </div>
        ${c.explanation ? `
        <div class="complexity-item" style="max-width:300px">
          <span class="complexity-label">Note</span>
          <span style="font-size:0.8rem;color:var(--text-muted)">${escapeHtml(c.explanation.slice(0,120))}</span>
        </div>` : ''}
      </div>`;
  }

  // Follow-up suggestion chips
  const suggestions = (extra.suggestions || []).filter(s => s && s.length > 4);
  if (suggestions.length) {
    const chips = suggestions
      .map(s => `<button class="suggestion-chip" onclick="useSuggestion(this)">${escapeHtml(s)}</button>`)
      .join('');
    extras += `<div class="suggestions">${chips}</div>`;
  }

  wrap.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">
      ${bubble}
      ${extras}
    </div>`;

  container.appendChild(wrap);
  scrollToBottom();
  return wrap;
}

function addTypingIndicator() {
  const container = document.getElementById('messages');
  const d = document.createElement('div');
  d.id = 'typing';
  d.className = 'message assistant';
  d.innerHTML = `
    <div class="message-avatar">⚡</div>
    <div class="message-content">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;
  container.appendChild(d);
  scrollToBottom();
}
function removeTypingIndicator() {
  const el = document.getElementById('typing');
  if (el) el.remove();
}

/* ============================================================
   Send message
   ============================================================ */
async function sendMessage() {
  if (isLoading) return;
  const input = document.getElementById('msg-input');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  input.style.height = 'auto';
  renderMessage('user', message);
  addTypingIndicator();
  isLoading = true;
  document.getElementById('send-btn').disabled = true;

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: SESSION_ID, streaming: false }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    removeTypingIndicator();
    renderMessage('assistant', data.response, {
      complexity: data.complexity,
      suggestions: data.follow_up_suggestions,
    });
    loadSidebarSessions();

  } catch {
    removeTypingIndicator();
    showToast('Failed to send message. Please try again.');
  } finally {
    isLoading = false;
    document.getElementById('send-btn').disabled = false;
    input.focus();
  }
}

function useSuggestion(btn) {
  const input = document.getElementById('msg-input');
  input.value = btn.textContent.trim();
  input.focus();
  sendMessage();
}

/* ============================================================
   Load existing conversation history
   ============================================================ */
async function loadHistory() {
  try {
    const res = await fetch(`/api/sessions/${SESSION_ID}/history`);
    if (!res.ok) return;
    const data = await res.json();
    const history = (data.history || []).filter(m => m.role !== 'system');

    if (!history.length) return; // leave welcome screen

    const container = document.getElementById('messages');
    container.innerHTML = '';
    for (const msg of history) {
      if (msg.role === 'user' || msg.role === 'assistant') {
        renderMessage(msg.role, msg.content);
      }
    }
  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

/* ============================================================
   Sidebar — recent sessions
   ============================================================ */
async function loadSidebarSessions() {
  const container = document.getElementById('sidebar-sessions');
  try {
    const res = await fetch('/api/sessions');
    if (!res.ok) return;
    const sessions = await res.json();

    if (!sessions.length) {
      container.innerHTML = '<div class="sidebar-empty">No previous chats</div>';
      return;
    }

    container.innerHTML = sessions.map(s => `
      <a href="/chat/${s.session_id}"
         class="sidebar-session-item ${s.session_id === SESSION_ID ? 'active' : ''}">
        <div class="sidebar-session-title">${escapeHtml((s.title || 'Chat').slice(0, 55))}</div>
        <div class="sidebar-session-date">${formatDate(s.last_accessed)}</div>
      </a>`).join('');

  } catch (err) {
    console.error('Failed to load sidebar sessions:', err);
  }
}

/* ============================================================
   Input auto-resize + Enter key handler
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('msg-input');

  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 160) + 'px';
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  loadHistory();
  loadSidebarSessions();
  input.focus();
});

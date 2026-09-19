/* sessions.js — algo_pal sessions list page */

function formatDate(dateStr) {
  if (!dateStr) return '';
  try {
    return new Date(dateStr).toLocaleString(undefined, {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch { return ''; }
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(text || ''));
  return d.innerHTML;
}

async function loadSessions() {
  const grid  = document.getElementById('sessions-grid');
  const empty = document.getElementById('empty-state');

  // Skeleton placeholders
  grid.innerHTML = [0, 1, 2].map(() => `
    <div class="loading-skeleton">
      <div class="skeleton-line medium"></div>
      <div class="skeleton-line short" style="margin-top:14px"></div>
    </div>
  `).join('');

  try {
    const res = await fetch('/api/sessions');
    if (!res.ok) throw new Error();
    const sessions = await res.json();

    grid.innerHTML = '';

    if (!sessions.length) {
      empty.hidden = false;
      return;
    }

    grid.innerHTML = sessions.map(s => `
      <a class="session-card" href="/chat/${s.session_id}">
        <div class="session-card-header">
          <div class="session-title">${escapeHtml(s.title)}</div>
          <button
            class="session-delete"
            onclick="deleteSession(event, '${s.session_id}')"
            title="Delete conversation"
          >✕</button>
        </div>
        <div class="session-meta">
          <span class="session-meta-badge">${s.message_count} msg${s.message_count !== 1 ? 's' : ''}</span>
          <span>${formatDate(s.last_accessed)}</span>
        </div>
      </a>
    `).join('');

  } catch {
    grid.innerHTML = '<p style="color:var(--danger);padding:20px">Failed to load sessions.</p>';
  }
}

async function deleteSession(event, sessionId) {
  event.preventDefault();
  event.stopPropagation();
  if (!confirm('Delete this conversation?')) return;
  try {
    const res = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    loadSessions();
  } catch {
    alert('Failed to delete session.');
  }
}

document.addEventListener('DOMContentLoaded', loadSessions);

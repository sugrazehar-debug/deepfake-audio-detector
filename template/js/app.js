/**
 * DeepGuard Pro - Common JavaScript Utilities
 * Base URL: http://127.0.0.1:8000
 */

const BASE_URL = 'http://127.0.0.1:8000';

/* ============================================================
   AUTH GUARD
   ============================================================ */
function authGuard() {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = '/template/login.html';
    return false;
  }
  return true;
}

/* ============================================================
   API FETCH WITH AUTH
   ============================================================ */
async function apiFetch(endpoint, options) {
  const token = localStorage.getItem('token');
  const url = BASE_URL + endpoint;

  const defaultOptions = {
    headers: {
      'Authorization': 'Bearer ' + token,
      ...(options && options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' })
    }
  };

  try {
    const response = await fetch(url, { ...defaultOptions, ...options });
    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      window.location.href = '/template/login.html';
      return null;
    }
    return response;
  } catch (error) {
    showToast('Network error: ' + error.message, 'error');
    throw error;
  }
}

/* ============================================================
   TOAST NOTIFICATIONS
   ============================================================ */
function showToast(message, type) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(function() {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(function() { toast.remove(); }, 300);
  }, 4000);
}

/* ============================================================
   LOGOUT
   ============================================================ */
function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  window.location.href = '/template/login.html';
}

/* ============================================================
   FORMAT DATE
   ============================================================ */
function formatDate(dateStr) {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/* ============================================================
   FORMAT CONFIDENCE
   ============================================================ */
function formatConfidence(value) {
  if (value === null || value === undefined || isNaN(value)) return '0%';
  if (typeof value === 'string' && value.includes('%')) return value;
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0%';
  return (num * 100).toFixed(2) + '%';
}

/* ============================================================
   GET IMAGE URL WITH FALLBACK
   ============================================================ */
function getImageUrl(path, fallbackUid, type) {
  if (path) {
    return BASE_URL + '/' + path;
  }
  if (fallbackUid && type) {
    return BASE_URL + '/outputs/' + fallbackUid + '_' + type + '.png';
  }
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="200"%3E%3Crect fill="%231e293b" width="400" height="200"/%3E%3Ctext fill="%2394a3b8" font-family="sans-serif" font-size="16" dy=".3em" text-anchor="middle" x="200" y="100"%3EImage not available%3C/text%3E%3C/svg%3E';
}

/* ============================================================
   GET REPORT URL
   ============================================================ */
function getReportUrl(path) {
  if (!path) return '#';
  return BASE_URL + path;
}

/* ============================================================
   SIDEBAR ACTIVE STATE
   ============================================================ */
function setActiveNav(pageName) {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(function(item) {
    item.classList.remove('active');
    if (item.dataset.page === pageName) {
      item.classList.add('active');
    }
  });
}

/* ============================================================
   RENDER SIDEBAR USER
   ============================================================ */
function renderSidebarUser() {
  const username = localStorage.getItem('username') || 'User';
  const el = document.getElementById('sidebar-username');
  if (el) el.textContent = username;
  const av = document.getElementById('sidebar-avatar');
  if (av) av.textContent = username.charAt(0).toUpperCase();
}


/* Centralised API client. All pages import this. */
const API_BASE = (function () {
  // Same-origin when served by Flask (:5000) or by nginx in Docker (:8080) —
  // both expose /api on the page's own origin, so cookies and CORS Just Work.
  // Only when the frontend is served by a standalone static server (e.g.
  // `python -m http.server`) do we fall back to talking to Flask directly,
  // which then requires a matching CORS_ORIGIN in backend/.env.
  const samePort = ['5000', '8080', '80', '443', ''].includes(window.location.port);
  return samePort ? '' : 'http://localhost:5000';
})();

async function api(path, options = {}) {
  const opts = {
    method: options.method || 'GET',
    headers: { ...(options.headers || {}) },
    credentials: 'include',
  };
  if (options.body !== undefined) {
    if (options.body instanceof FormData) {
      opts.body = options.body;
    } else {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(options.body);
    }
  }
  const res = await fetch(API_BASE + path, opts);
  let data = null;
  try { data = await res.json(); } catch (_) { /* no-op */ }
  if (!res.ok) {
    const msg = (data && (data.error || data.message)) || `HTTP ${res.status}`;
    const err = new Error(msg);
    err.status = res.status;
    err.details = data && data.details;
    throw err;
  }
  return data;
}

/* ---------------- UI helpers ---------------- */
function toast(message, type = '') {
  let el = document.getElementById('app-toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'app-toast';
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.className = `toast show ${type}`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.className = `toast ${type}`; }, 2800);
}

function imgUrl(path) {
  if (!path) return 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600';
  if (/^https?:/i.test(path)) return path;
  return API_BASE + path;
}

function formatPrice(value) {
  return '$' + Number(value).toLocaleString(undefined, {
    minimumFractionDigits: 2, maximumFractionDigits: 2,
  });
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

/* ---------------- Session helpers ---------------- */
async function getCurrentUser() {
  try {
    const data = await api('/api/auth/me');
    return data.user;
  } catch (_) {
    return null;
  }
}

async function requireAuth(redirect = 'login.html') {
  const user = await getCurrentUser();
  if (!user) { window.location.href = redirect; return null; }
  return user;
}

async function requireAdmin() {
  const user = await getCurrentUser();
  if (!user || user.role !== 'admin') {
    window.location.href = 'login.html';
    return null;
  }
  return user;
}

async function logout() {
  try { await api('/api/auth/logout', { method: 'POST' }); } catch (_) {}
  window.location.href = 'index.html';
}

/* ---------------- Header injection ---------------- */
async function renderHeader(active = '') {
  const user = await getCurrentUser();
  const cartSize = user ? await getCartSize() : 0;
  const html = `
    <header class="site-header">
      <div class="container">
        <a href="index.html" class="brand">
          <span class="brand-main">THE JEWEL <span class="brand-accent">NEST</span></span>
          <span class="brand-sub">Studio</span>
        </a>
        <button class="menu-toggle" id="menu-toggle" aria-label="Menu">☰</button>
        <ul class="nav-links" id="nav-links">
          <li><a href="index.html"   class="${active === 'home' ? 'active' : ''}">Home</a></li>
          <li><a href="products.html" class="${active === 'shop' ? 'active' : ''}">Shop</a></li>
          ${user ? `<li><a href="orders.html" class="${active === 'orders' ? 'active' : ''}">Orders</a></li>` : ''}
          ${user && user.role === 'admin' ? `<li><a href="admin.html" class="${active === 'admin' ? 'active' : ''}">Admin</a></li>` : ''}
        </ul>
        <div class="nav-actions">
          ${user
            ? `<a href="cart.html">Cart <span class="cart-badge" id="cart-badge">${cartSize}</span></a>
               <button id="logout-btn">Logout</button>`
            : `<a href="login.html">Login</a>
               <a href="register.html">Register</a>`}
        </div>
      </div>
    </header>`;
  const slot = document.getElementById('header-slot');
  if (slot) slot.innerHTML = html;

  const tgl = document.getElementById('menu-toggle');
  if (tgl) tgl.onclick = () => document.getElementById('nav-links').classList.toggle('open');
  const lo = document.getElementById('logout-btn');
  if (lo) lo.onclick = logout;
}

function renderFooter() {
  const slot = document.getElementById('footer-slot');
  if (!slot) return;
  slot.innerHTML = `
    <footer class="site-footer">
      <div class="container">
        <div class="grid">
          <div>
            <div class="brand" style="color:#fff">
              <span class="brand-main">THE JEWEL <span class="brand-accent">NEST</span></span>
              <span class="brand-sub">Studio</span>
            </div>
            <p style="margin-top:1rem;max-width:320px;font-size:.9rem;color:#aaa">
              Heirloom-quality jewelry crafted with conscience and elegance.
            </p>
            <div class="social-row">
              <a href="https://www.instagram.com/_the_jewelnest_studio__" target="_blank" rel="noopener" aria-label="Instagram" title="Instagram">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M12 2.2c3.2 0 3.6 0 4.85.07 1.17.05 1.8.25 2.23.42.56.22.96.48 1.38.9.42.42.68.82.9 1.38.17.42.37 1.06.42 2.23.07 1.25.07 1.65.07 4.85s0 3.6-.07 4.85c-.05 1.17-.25 1.8-.42 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.17-1.06.37-2.23.42-1.25.07-1.65.07-4.85.07s-3.6 0-4.85-.07c-1.17-.05-1.8-.25-2.23-.42a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.17-.42-.37-1.06-.42-2.23C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.85c.05-1.17.25-1.8.42-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.17 1.06-.37 2.23-.42C8.4 2.2 8.8 2.2 12 2.2zm0 1.95c-3.15 0-3.52 0-4.76.07-1.07.05-1.65.23-2.04.38-.51.2-.88.44-1.27.83-.39.39-.63.76-.83 1.27-.15.39-.33.97-.38 2.04-.07 1.24-.07 1.61-.07 4.76s0 3.52.07 4.76c.05 1.07.23 1.65.38 2.04.2.51.44.88.83 1.27.39.39.76.63 1.27.83.39.15.97.33 2.04.38 1.24.07 1.61.07 4.76.07s3.52 0 4.76-.07c1.07-.05 1.65-.23 2.04-.38.51-.2.88-.44 1.27-.83.39-.39.63-.76.83-1.27.15-.39.33-.97.38-2.04.07-1.24.07-1.61.07-4.76s0-3.52-.07-4.76c-.05-1.07-.23-1.65-.38-2.04a3.42 3.42 0 0 0-.83-1.27 3.42 3.42 0 0 0-1.27-.83c-.39-.15-.97-.33-2.04-.38-1.24-.07-1.61-.07-4.76-.07zm0 3.32a4.53 4.53 0 1 1 0 9.06 4.53 4.53 0 0 1 0-9.06zm0 1.95a2.58 2.58 0 1 0 0 5.16 2.58 2.58 0 0 0 0-5.16zm5.78-2.17a1.06 1.06 0 1 1-2.12 0 1.06 1.06 0 0 1 2.12 0z"/></svg>
              </a>
              <a href="https://youtube.com/@jewelnest-v4h" target="_blank" rel="noopener" aria-label="YouTube" title="YouTube">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2C0 8.1 0 12 0 12s0 3.9.5 5.8a3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1c.5-1.9.5-5.8.5-5.8s0-3.9-.5-5.8zM9.6 15.6V8.4l6.3 3.6-6.3 3.6z"/></svg>
              </a>
            </div>
          </div>
          <div>
            <h4>Shop</h4>
            <ul>
              <li><a href="products.html?category=Rings">Rings</a></li>
              <li><a href="products.html?category=Necklaces">Necklaces</a></li>
              <li><a href="products.html?category=Earrings">Earrings</a></li>
              <li><a href="products.html?category=Bracelets">Bracelets</a></li>
            </ul>
          </div>
          <div>
            <h4>Help</h4>
            <ul>
              <li><a href="#">Shipping</a></li>
              <li><a href="#">Returns</a></li>
              <li><a href="#">Care Guide</a></li>
            </ul>
          </div>
          <div>
            <h4>Company</h4>
            <ul>
              <li><a href="#">About</a></li>
              <li><a href="#">Stores</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
        </div>
        <div class="copy">© ${new Date().getFullYear()} The Jewel Nest Studio. All rights reserved.</div>
      </div>
    </footer>`;
}

async function getCartSize() {
  try {
    const data = await api('/api/cart');
    return (data.items || []).reduce((n, x) => n + x.quantity, 0);
  } catch (_) { return 0; }
}

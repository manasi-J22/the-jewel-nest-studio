/* Admin panel — products, orders, expenses */

let _allProducts = [];

/* ---------- Tab switching ---------- */
function switchTab(name) {
  document.querySelectorAll('.admin-tab').forEach(s => s.hidden = s.id !== `tab-${name}`);
  document.querySelectorAll('.admin-nav').forEach(a =>
    a.classList.toggle('active', a.dataset.tab === name));
  if (name === 'dashboard') loadDashboard();
  if (name === 'products')  loadProducts();
  if (name === 'orders')    loadOrders();
  if (name === 'expenses')  loadExpenses();
}

function bindTabs() {
  document.querySelectorAll('.admin-nav').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      switchTab(a.dataset.tab);
      window.location.hash = a.dataset.tab;
    });
  });
}

/* ---------- Dashboard ---------- */
async function loadDashboard() {
  try {
    const stats = await api('/api/admin/stats');
    document.getElementById('stats-grid').innerHTML = `
      ${statCard('Total Users', stats.users)}
      ${statCard('Products', stats.products)}
      ${statCard('Orders', stats.orders)}
      ${statCard('Pending', stats.pending_orders)}
      ${statCard('Revenue', formatPrice(stats.revenue))}
    `;
    const orders = (await api('/api/admin/orders')).orders.slice(0, 8);
    document.getElementById('recent-orders').innerHTML = orders.length
      ? `<div class="table-wrap"><table class="data">
          <thead><tr><th>#</th><th>Customer</th><th>Total</th><th>Status</th><th>Date</th></tr></thead>
          <tbody>${orders.map(o => `
            <tr>
              <td>#${o.id}</td>
              <td>${escapeHtml(o.user_name)}<br><span class="muted small">${escapeHtml(o.user_email)}</span></td>
              <td>${formatPrice(o.total)}</td>
              <td><span class="badge ${o.status}">${o.status}</span></td>
              <td>${new Date(o.created_at).toLocaleDateString()}</td>
            </tr>`).join('')}</tbody></table></div>`
      : '<p class="empty">No orders yet.</p>';
  } catch (e) { toast(e.message, 'error'); }
}

function statCard(label, value) {
  return `<div class="stat-card"><div class="label">${label}</div><div class="value">${value}</div></div>`;
}

/* ---------- Products ---------- */
async function loadProducts() {
  try {
    const data = await api('/api/products?limit=200');
    _allProducts = data.products;
    const tb = document.querySelector('#products-table tbody');
    tb.innerHTML = data.products.map(p => `
      <tr>
        <td><img src="${imgUrl(p.image_url)}" style="width:50px;height:50px;object-fit:cover;border-radius:4px"></td>
        <td>${escapeHtml(p.name)}</td>
        <td>${escapeHtml(p.category)}</td>
        <td>${formatPrice(p.price)}</td>
        <td>${p.stock}</td>
        <td>
          <button class="btn btn-sm btn-outline" data-edit="${p.id}">Edit</button>
          <button class="btn btn-sm" style="background:var(--error);border-color:var(--error)" data-del="${p.id}">Delete</button>
        </td>
      </tr>`).join('') || '<tr><td colspan="6" class="empty">No products yet.</td></tr>';

    tb.querySelectorAll('[data-edit]').forEach(b =>
      b.onclick = () => editProduct(+b.dataset.edit));
    tb.querySelectorAll('[data-del]').forEach(b =>
      b.onclick = () => deleteProduct(+b.dataset.del));
  } catch (e) { toast(e.message, 'error'); }
}

function bindProductForm() {
  const form = document.getElementById('product-form');
  document.getElementById('reset-product-form').onclick = () => {
    form.reset(); form.id.value = '';
    document.getElementById('product-form-title').textContent = 'Add Product';
  };
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('product-form-error');
    errEl.textContent = '';
    const id = form.id.value;
    const fd = new FormData(form);
    if (!fd.get('image') || !fd.get('image').name) fd.delete('image');
    fd.delete('id');
    try {
      const url = id ? `/api/admin/products/${id}` : '/api/admin/products';
      await api(url, { method: 'POST', body: fd });
      toast(id ? 'Product updated' : 'Product created', 'success');
      form.reset(); form.id.value = '';
      document.getElementById('product-form-title').textContent = 'Add Product';
      loadProducts();
    } catch (err) {
      errEl.textContent = err.message + (err.details ? ' — ' + JSON.stringify(err.details) : '');
    }
  });
}

function editProduct(id) {
  const p = _allProducts.find(x => x.id === id);
  if (!p) return;
  const form = document.getElementById('product-form');
  form.id.value       = p.id;
  form.name.value     = p.name;
  form.category.value = p.category;
  form.price.value    = p.price;
  form.stock.value    = p.stock;
  form.material.value = p.material || '';
  form.description.value = p.description || '';
  document.getElementById('product-form-title').textContent = `Edit Product #${p.id}`;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function deleteProduct(id) {
  if (!confirm('Delete this product?')) return;
  try {
    await api(`/api/admin/products/${id}`, { method: 'DELETE' });
    toast('Deleted', 'success');
    loadProducts();
  } catch (e) { toast(e.message, 'error'); }
}

/* ---------- Orders ---------- */
const ORDER_STATUSES = ['pending', 'processing', 'shipped', 'delivered', 'cancelled'];

async function loadOrders() {
  try {
    const data = await api('/api/admin/orders');
    const tb = document.querySelector('#orders-table tbody');
    tb.innerHTML = data.orders.map(o => `
      <tr>
        <td>#${o.id}</td>
        <td>${escapeHtml(o.user_name)}<br><span class="muted small">${escapeHtml(o.user_email)}</span></td>
        <td>${o.items.map(it => `${escapeHtml(it.product_name)} × ${it.quantity}`).join('<br>')}</td>
        <td>${formatPrice(o.total)}</td>
        <td>
          <select data-status="${o.id}">
            ${ORDER_STATUSES.map(s => `<option value="${s}" ${s === o.status ? 'selected' : ''}>${s}</option>`).join('')}
          </select>
        </td>
        <td>${new Date(o.created_at).toLocaleString()}</td>
        <td><button class="btn btn-sm" data-save="${o.id}">Save</button></td>
      </tr>`).join('') || '<tr><td colspan="7" class="empty">No orders yet.</td></tr>';
    tb.querySelectorAll('[data-save]').forEach(b =>
      b.onclick = () => saveOrderStatus(+b.dataset.save));
  } catch (e) { toast(e.message, 'error'); }
}

async function saveOrderStatus(orderId) {
  const sel = document.querySelector(`#orders-table select[data-status="${orderId}"]`);
  try {
    await api(`/api/admin/orders/${orderId}/status`, {
      method: 'PUT', body: { status: sel.value },
    });
    toast('Order updated', 'success');
  } catch (e) { toast(e.message, 'error'); }
}

/* ---------- Expenses ---------- */
async function loadExpenses() {
  populateYearSelect();
  await Promise.all([loadExpenseSummary(), loadExpenseList()]);
}

function populateYearSelect() {
  const sel = document.getElementById('exp-year');
  if (sel.options.length) return;
  const now = new Date().getFullYear();
  for (let y = now; y >= now - 4; y--) {
    sel.add(new Option(y, y, y === now, y === now));
  }
  sel.onchange = loadExpenseSummary;
}

async function loadExpenseSummary() {
  const year = +document.getElementById('exp-year').value;
  try {
    const d = await api(`/api/admin/expenses/dashboard?year=${year}`);
    document.getElementById('exp-summary').innerHTML = `
      ${statCard(`${year} Total`, formatPrice(d.total))}
      ${statCard('Categories', d.by_type.length)}
      ${statCard('Top Category', d.by_type[0] ? d.by_type[0].expense_type : '—')}
    `;
    const max = Math.max(...d.monthly.map(m => m.total), 1);
    const months = Array(12).fill(0);
    d.monthly.forEach(m => { months[m.month - 1] = m.total; });
    const labels = ['J','F','M','A','M','J','J','A','S','O','N','D'];
    document.getElementById('monthly-bars').innerHTML = months.map((v, i) => `
      <div class="bar" style="height:${(v / max * 100).toFixed(1)}%" title="${labels[i]}: ${formatPrice(v)}">
        ${v ? `<span class="value">${v >= 1000 ? '$' + (v/1000).toFixed(1) + 'k' : '$' + v.toFixed(0)}</span>` : ''}
        <span class="label">${labels[i]}</span>
      </div>`).join('');
  } catch (e) { toast(e.message, 'error'); }
}

async function loadExpenseList() {
  try {
    const d = await api('/api/admin/expenses');
    const tb = document.querySelector('#expense-table tbody');
    tb.innerHTML = d.expenses.map(e => `
      <tr>
        <td>${e.expense_date}</td>
        <td>${escapeHtml(e.expense_type)}</td>
        <td>${formatPrice(e.amount)}</td>
        <td>${escapeHtml(e.note || '')}</td>
        <td><button class="btn btn-sm" style="background:var(--error);border-color:var(--error)" data-del-exp="${e.id}">Delete</button></td>
      </tr>`).join('') || '<tr><td colspan="5" class="empty">No expenses yet.</td></tr>';
    tb.querySelectorAll('[data-del-exp]').forEach(b =>
      b.onclick = () => deleteExpense(+b.dataset.delExp));
  } catch (e) { toast(e.message, 'error'); }
}

async function deleteExpense(id) {
  if (!confirm('Delete this expense?')) return;
  try {
    await api(`/api/admin/expenses/${id}`, { method: 'DELETE' });
    toast('Deleted', 'success');
    loadExpenses();
  } catch (e) { toast(e.message, 'error'); }
}

function bindExpenseForm() {
  const form = document.getElementById('expense-form');
  form.expense_date.value = new Date().toISOString().split('T')[0];
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
      expense_type: form.expense_type.value.trim(),
      amount: form.amount.value,
      expense_date: form.expense_date.value,
      note: form.note.value.trim() || null,
    };
    try {
      await api('/api/admin/expenses', { method: 'POST', body });
      toast('Expense added', 'success');
      form.reset();
      form.expense_date.value = new Date().toISOString().split('T')[0];
      loadExpenses();
    } catch (err) { toast(err.message, 'error'); }
  });
}

/* ---------- Boot ---------- */
document.addEventListener('DOMContentLoaded', async () => {
  await renderHeader('admin');
  const user = await requireAdmin();
  if (!user) return;
  bindTabs();
  bindProductForm();
  bindExpenseForm();
  const initial = (window.location.hash || '#dashboard').slice(1);
  switchTab(['dashboard','products','orders','expenses'].includes(initial) ? initial : 'dashboard');
});

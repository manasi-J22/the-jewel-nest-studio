/* Order history */

async function loadOrders() {
  const root = document.getElementById('orders-root');
  try {
    const data = await api('/api/orders');
    if (!data.orders.length) {
      root.innerHTML = `
        <div class="empty">
          <h2 style="margin-bottom:1rem">No orders yet</h2>
          <a class="btn" href="products.html">Start Shopping</a>
        </div>`;
      return;
    }
    root.innerHTML = data.orders.map(o => orderCardHtml(o)).join('');
  } catch (e) {
    root.innerHTML = `<p class="empty">${escapeHtml(e.message)}</p>`;
  }
}

function orderCardHtml(o) {
  return `
    <article class="order-card">
      <header>
        <div>
          <div class="muted small">Order #${o.id}</div>
          <div class="muted small">${new Date(o.created_at).toLocaleString()}</div>
        </div>
        <span class="badge ${o.status}">${o.status}</span>
      </header>
      <div class="order-items">
        ${o.items.map(it => `
          <div class="order-item">
            <span>${escapeHtml(it.product_name)} × ${it.quantity}</span>
            <span>${formatPrice(it.unit_price * it.quantity)}</span>
          </div>`).join('')}
      </div>
      <footer>
        <div class="muted small">${escapeHtml(o.address)}</div>
        <div><strong>Total: ${formatPrice(o.total)}</strong></div>
      </footer>
    </article>`;
}

document.addEventListener('DOMContentLoaded', async () => {
  await renderHeader('orders');
  renderFooter();
  const user = await requireAuth();
  if (!user) return;
  if (new URLSearchParams(window.location.search).get('placed')) {
    toast('Order placed successfully', 'success');
  }
  loadOrders();
});

/* Checkout flow */

async function loadSummary() {
  const root = document.getElementById('checkout-summary');
  try {
    const data = await api('/api/cart');
    if (!data.items.length) {
      window.location.href = 'cart.html';
      return;
    }
    root.innerHTML = `
      <h3>Your Order</h3>
      <ul class="co-items">
        ${data.items.map(it => `
          <li>
            <img src="${imgUrl(it.image_url)}" alt="">
            <div>
              <div>${escapeHtml(it.name)}</div>
              <div class="muted">Qty: ${it.quantity}</div>
            </div>
            <div>${formatPrice(it.line_total)}</div>
          </li>`).join('')}
      </ul>
      <div class="row total"><span>Total</span><span>${formatPrice(data.total)}</span></div>`;
  } catch (e) { root.innerHTML = `<p class="empty">${escapeHtml(e.message)}</p>`; }
}

function bindForm() {
  const form = document.getElementById('checkout-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('co-error');
    errEl.textContent = '';
    const body = {
      address: form.address.value.trim(),
      phone: form.phone.value.trim(),
      payment_method: form.payment_method.value,
    };
    try {
      const res = await api('/api/orders/checkout', { method: 'POST', body });
      toast('Order placed', 'success');
      setTimeout(() => { window.location.href = `orders.html?placed=${res.order_id}`; }, 600);
    } catch (err) {
      errEl.textContent = err.message;
    }
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  await renderHeader();
  renderFooter();
  const user = await requireAuth();
  if (!user) return;
  loadSummary();
  bindForm();
});

/* Shopping cart page */

async function loadCart() {
  const root = document.getElementById('cart-root');
  try {
    const data = await api('/api/cart');
    if (!data.items.length) {
      root.innerHTML = `
        <div class="empty">
          <h2 style="margin-bottom:1rem">Your cart is empty</h2>
          <a class="btn" href="products.html">Continue Shopping</a>
        </div>`;
      return;
    }
    root.innerHTML = `
      <div class="cart-grid">
        <div class="cart-items">
          ${data.items.map(it => cartItemHtml(it)).join('')}
        </div>
        <aside class="cart-summary">
          <h3>Order Summary</h3>
          <div class="row"><span>Subtotal</span><span>${formatPrice(data.total)}</span></div>
          <div class="row muted"><span>Shipping</span><span>Free</span></div>
          <div class="row total"><span>Total</span><span>${formatPrice(data.total)}</span></div>
          <a class="btn btn-gold btn-block" href="checkout.html">Checkout</a>
          <a class="btn btn-outline btn-block" href="products.html" style="margin-top:.75rem">Continue Shopping</a>
        </aside>
      </div>`;
    bindCartEvents();
  } catch (e) {
    root.innerHTML = `<p class="empty">${escapeHtml(e.message)}</p>`;
  }
}

function cartItemHtml(it) {
  return `
    <div class="cart-row" data-id="${it.product_id}">
      <img src="${imgUrl(it.image_url)}" alt="${escapeHtml(it.name)}">
      <div class="cart-row-info">
        <h4><a href="product-details.html?id=${it.product_id}">${escapeHtml(it.name)}</a></h4>
        <div class="muted">${formatPrice(it.price)} each</div>
      </div>
      <div class="qty-control">
        <button data-action="dec">−</button>
        <input type="number" value="${it.quantity}" min="1" max="${it.stock}" data-qty>
        <button data-action="inc">+</button>
      </div>
      <div class="line-total">${formatPrice(it.line_total)}</div>
      <button class="remove-btn" data-action="remove" aria-label="Remove">×</button>
    </div>`;
}

function bindCartEvents() {
  document.querySelectorAll('.cart-row').forEach(row => {
    const id = +row.dataset.id;
    const qtyInput = row.querySelector('[data-qty]');
    row.querySelector('[data-action="dec"]').onclick = () => updateQty(id, Math.max(1, +qtyInput.value - 1));
    row.querySelector('[data-action="inc"]').onclick = () => updateQty(id, +qtyInput.value + 1);
    qtyInput.onchange = () => updateQty(id, Math.max(1, +qtyInput.value));
    row.querySelector('[data-action="remove"]').onclick = () => removeItem(id);
  });
}

async function updateQty(productId, quantity) {
  try {
    await api('/api/cart/update', {
      method: 'POST', body: { product_id: productId, quantity },
    });
    loadCart();
  } catch (e) { toast(e.message, 'error'); }
}

async function removeItem(productId) {
  try {
    await api(`/api/cart/remove/${productId}`, { method: 'POST' });
    toast('Removed from cart');
    loadCart();
  } catch (e) { toast(e.message, 'error'); }
}

document.addEventListener('DOMContentLoaded', async () => {
  await renderHeader();
  renderFooter();
  const user = await requireAuth();
  if (user) loadCart();
});

/* Product details — gallery, add to cart, reviews */

let currentProduct = null;
let currentUser = null;

async function loadProduct() {
  const id = new URLSearchParams(window.location.search).get('id');
  if (!id) { document.getElementById('pd-root').innerHTML = '<p class="empty">No product specified.</p>'; return; }
  try {
    const data = await api(`/api/products/${id}`);
    currentProduct = data.product;
    render();
  } catch (e) {
    document.getElementById('pd-root').innerHTML = `<p class="empty">${escapeHtml(e.message)}</p>`;
  }
}

function render() {
  const p = currentProduct;
  const root = document.getElementById('pd-root');
  const inStock = p.stock > 0;
  root.innerHTML = `
    <div class="pd-grid">
      <div class="pd-img">
        <img src="${imgUrl(p.image_url)}" alt="${escapeHtml(p.name)}">
      </div>
      <div class="pd-info">
        <div class="cat">${escapeHtml(p.category)}</div>
        <h1>${escapeHtml(p.name)}</h1>
        ${p.review_count
          ? `<div class="rating-line">★ ${p.avg_rating.toFixed(1)} <span>(${p.review_count} reviews)</span></div>`
          : `<div class="rating-line"><span>No reviews yet</span></div>`}
        <div class="pd-price">${formatPrice(p.price)}</div>
        ${p.material ? `<div class="meta"><strong>Material:</strong> ${escapeHtml(p.material)}</div>` : ''}
        <p class="pd-desc">${escapeHtml(p.description || '')}</p>
        <div class="pd-stock ${inStock ? 'ok' : 'out'}">
          ${inStock ? `In stock — ${p.stock} available` : 'Out of stock'}
        </div>
        <div class="pd-actions">
          <input type="number" id="qty" value="1" min="1" max="${p.stock || 1}" ${inStock ? '' : 'disabled'}>
          <button class="btn btn-gold" id="add-cart-btn" ${inStock ? '' : 'disabled'}>Add to Cart</button>
        </div>
      </div>
    </div>

    <section class="pd-reviews">
      <h2>Reviews</h2>
      <div id="review-form-slot"></div>
      <div id="review-list">
        ${p.reviews.length ? p.reviews.map(r => reviewHtml(r)).join('') : '<p class="empty">No reviews yet — be the first.</p>'}
      </div>
    </section>
  `;
  document.getElementById('add-cart-btn')?.addEventListener('click', addToCart);
  renderReviewForm();
}

function reviewHtml(r) {
  const stars = '★'.repeat(r.rating) + '☆'.repeat(5 - r.rating);
  return `
    <article class="review">
      <div class="review-head">
        <strong>${escapeHtml(r.user_name)}</strong>
        <span class="stars">${stars}</span>
        <span class="date">${new Date(r.created_at).toLocaleDateString()}</span>
      </div>
      ${r.comment ? `<p>${escapeHtml(r.comment)}</p>` : ''}
    </article>`;
}

async function renderReviewForm() {
  const slot = document.getElementById('review-form-slot');
  if (!currentUser) {
    slot.innerHTML = '<p class="login-hint"><a href="login.html">Log in</a> to leave a review.</p>';
    return;
  }
  slot.innerHTML = `
    <form id="review-form" class="review-form">
      <h3>Leave a review</h3>
      <div class="stars-input" id="stars-input">
        ${[1,2,3,4,5].map(i => `<button type="button" data-v="${i}">☆</button>`).join('')}
      </div>
      <input type="hidden" name="rating" id="rating" value="0">
      <div class="field">
        <textarea name="comment" placeholder="Share your thoughts…" maxlength="1000"></textarea>
      </div>
      <button class="btn btn-sm" type="submit">Submit Review</button>
      <div class="error-text" id="review-err"></div>
    </form>`;
  const stars = document.querySelectorAll('#stars-input button');
  stars.forEach(btn => {
    btn.onclick = () => {
      const v = +btn.dataset.v;
      document.getElementById('rating').value = v;
      stars.forEach(b => b.textContent = (+b.dataset.v <= v) ? '★' : '☆');
    };
  });
  document.getElementById('review-form').onsubmit = async (e) => {
    e.preventDefault();
    const rating = +document.getElementById('rating').value;
    const comment = e.target.comment.value.trim();
    const errEl = document.getElementById('review-err');
    if (!rating) { errEl.textContent = 'Please pick a rating'; return; }
    try {
      await api('/api/reviews', {
        method: 'POST',
        body: { product_id: currentProduct.id, rating, comment },
      });
      toast('Thanks for your review', 'success');
      loadProduct();
    } catch (err) {
      errEl.textContent = err.message;
    }
  };
}

async function addToCart() {
  if (!currentUser) { window.location.href = 'login.html'; return; }
  const qty = Math.max(1, parseInt(document.getElementById('qty').value, 10) || 1);
  try {
    await api('/api/cart/add', {
      method: 'POST',
      body: { product_id: currentProduct.id, quantity: qty },
    });
    toast('Added to cart', 'success');
    const badge = document.getElementById('cart-badge');
    if (badge) badge.textContent = await getCartSize();
  } catch (e) {
    toast(e.message, 'error');
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  await renderHeader('shop');
  renderFooter();
  currentUser = await getCurrentUser();
  loadProduct();
});

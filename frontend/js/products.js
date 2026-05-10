/* Product listing with filters */

const state = {
  category: '',
  min_price: '',
  max_price: '',
  search: '',
  sort: 'newest',
};

function readQuery() {
  const q = new URLSearchParams(window.location.search);
  state.category = q.get('category') || '';
  state.search   = q.get('search') || '';
}

async function populateCategories() {
  try {
    const data = await api('/api/products/categories');
    const sel = document.getElementById('f-category');
    sel.innerHTML = '<option value="">All Categories</option>' +
      data.categories.map(c =>
        `<option value="${escapeHtml(c)}" ${c === state.category ? 'selected' : ''}>${escapeHtml(c)}</option>`
      ).join('');
  } catch (_) {}
}

async function loadProducts() {
  const root = document.getElementById('products-grid');
  root.innerHTML = Array(8).fill(0).map(() =>
    '<div class="product-card"><div class="img-wrap skeleton"></div>' +
    '<div class="product-body"><div class="skeleton" style="height:1.1rem;margin-bottom:.5rem"></div>' +
    '<div class="skeleton" style="height:.9rem;width:50%"></div></div></div>'
  ).join('');

  const params = new URLSearchParams();
  if (state.category)  params.set('category', state.category);
  if (state.min_price) params.set('min_price', state.min_price);
  if (state.max_price) params.set('max_price', state.max_price);
  if (state.search)    params.set('search', state.search);
  if (state.sort)      params.set('sort', state.sort);

  try {
    const data = await api('/api/products?' + params.toString());
    if (!data.products.length) {
      root.innerHTML = '<p class="empty" style="grid-column:1/-1">No products match your filters.</p>';
      return;
    }
    root.innerHTML = data.products.map(p => `
      <article class="product-card" data-id="${p.id}">
        <div class="img-wrap">
          <img src="${imgUrl(p.image_url)}" alt="${escapeHtml(p.name)}" loading="lazy">
        </div>
        <div class="product-body">
          <div class="cat">${escapeHtml(p.category)}</div>
          <h3>${escapeHtml(p.name)}</h3>
          <div class="price">${formatPrice(p.price)}</div>
          ${p.review_count ? `<div class="rating">★ ${p.avg_rating.toFixed(1)} (${p.review_count})</div>` : ''}
        </div>
      </article>
    `).join('');
    document.querySelectorAll('.product-card[data-id]').forEach(card => {
      card.onclick = () => { window.location.href = `product-details.html?id=${card.dataset.id}`; };
    });
  } catch (e) {
    root.innerHTML = `<p class="empty">${escapeHtml(e.message)}</p>`;
  }
}

function bindFilters() {
  document.getElementById('f-category').addEventListener('change', e => {
    state.category = e.target.value; loadProducts();
  });
  document.getElementById('f-sort').addEventListener('change', e => {
    state.sort = e.target.value; loadProducts();
  });
  document.getElementById('f-min').addEventListener('input', debounce(e => {
    state.min_price = e.target.value; loadProducts();
  }, 350));
  document.getElementById('f-max').addEventListener('input', debounce(e => {
    state.max_price = e.target.value; loadProducts();
  }, 350));
  const search = document.getElementById('f-search');
  search.value = state.search;
  search.addEventListener('input', debounce(e => {
    state.search = e.target.value; loadProducts();
  }, 350));
}

function debounce(fn, ms) {
  let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

document.addEventListener('DOMContentLoaded', async () => {
  await renderHeader('shop');
  renderFooter();
  readQuery();
  await populateCategories();
  bindFilters();
  loadProducts();
});

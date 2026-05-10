/* Home page — featured products & categories */

const CATEGORIES = [
  { name: 'Rings',
    img: 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600' },
  { name: 'Necklaces',
    img: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600' },
  { name: 'Earrings',
    img: 'https://images.unsplash.com/photo-1535632787350-4e68ef0ac584?w=600' },
  { name: 'Bracelets',
    img: 'https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=600' },
];

function renderCategories() {
  const root = document.getElementById('cat-grid');
  if (!root) return;
  root.innerHTML = CATEGORIES.map(c => `
    <a class="cat-card" href="products.html?category=${encodeURIComponent(c.name)}">
      <img src="${c.img}" alt="${escapeHtml(c.name)}" loading="lazy">
      <div class="cat-card-inner"><h3>${escapeHtml(c.name)}</h3></div>
    </a>
  `).join('');
}

async function loadFeatured() {
  const root = document.getElementById('featured-grid');
  if (!root) return;
  root.innerHTML = Array(4).fill(0).map(() =>
    '<div class="product-card"><div class="img-wrap skeleton"></div>' +
    '<div class="product-body"><div class="skeleton" style="height:1.1rem;margin-bottom:.5rem"></div>' +
    '<div class="skeleton" style="height:.9rem;width:50%"></div></div></div>'
  ).join('');
  try {
    const data = await api('/api/products?limit=8&sort=rating');
    if (!data.products.length) {
      root.innerHTML = '<p class="empty">No products yet — check back soon.</p>';
      return;
    }
    root.innerHTML = data.products.map(p => productCardHtml(p)).join('');
    bindProductCards();
  } catch (e) {
    root.innerHTML = `<p class="empty">Failed to load products. ${escapeHtml(e.message)}</p>`;
  }
}

function productCardHtml(p) {
  return `
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
    </article>`;
}

function bindProductCards() {
  document.querySelectorAll('.product-card[data-id]').forEach(card => {
    card.addEventListener('click', () => {
      window.location.href = `product-details.html?id=${card.dataset.id}`;
    });
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  await renderHeader('home');
  renderFooter();
  renderCategories();
  loadFeatured();
});

# The Jewel Nest Studio — Jewelry E-Commerce

A production-grade, full-stack e-commerce application for **The Jewel Nest
Studio**. Built as a clean, extendable base — not a toy demo.

🌐 Find us online:
[Instagram @\_the\_jewelnest\_studio\_\_](https://www.instagram.com/_the_jewelnest_studio__) ·
[YouTube @jewelnest-v4h](https://youtube.com/@jewelnest-v4h)

**Stack**

| Layer    | Tech                                    |
|----------|-----------------------------------------|
| Frontend | HTML / CSS / Vanilla JavaScript (no JS framework, no UI library) |
| Backend  | Python 3.11 + Flask 3                   |
| Database | MySQL 8                                 |
| Auth     | Session cookies, bcrypt password hashes |

## Features

- **Customer-facing**
  - Modern jewelry showcase home page
  - Product listing with category, price, search & sort filters
  - Product detail page with reviews and ratings
  - Server-side session cart, simulated checkout
  - Order history, status tracking
  - Customer reviews (one per product per user)
- **Admin panel**
  - Dashboard with KPIs and recent orders
  - CRUD products with image upload
  - Order management with status transitions
  - Expense tracker with monthly bar chart and category breakdown
- **Engineering**
  - Bcrypt + Flask-Session-based auth, role-based access
  - Marshmallow input validation, structured error responses
  - Rotating-file + console logging
  - MySQL connection pool, parameterized queries (SQL-injection safe)
  - Transactional checkout (stock decrement is atomic with order creation)
  - Dockerfile + docker-compose for one-command spin-up

## Project Layout

```
the-jewel-nest-studio/
├── backend/                  Flask app
│   ├── app.py                Application factory
│   ├── config.py             Env-driven config
│   ├── extensions.py         MySQL connection pool
│   ├── schema.sql            Full schema with indexes & FKs
│   ├── seed.py               Schema apply + sample data
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── models/               Raw-SQL data access
│   ├── routes/               Blueprints (auth, products, cart, …)
│   ├── services/             Business logic
│   └── utils/                Decorators, validators, logger
├── frontend/                 Static HTML/CSS/JS
│   ├── *.html                Pages
│   ├── css/
│   └── js/                   api.js + per-page scripts
├── Dockerfile                Bakes API + frontend into one image
├── docker-compose.yml        Local stack (MySQL + app)
├── .github/workflows/        CI + Docker Hub release pipelines
├── DOCKER.md                 Containerization & CI/CD guide
├── DEPLOY.md                 Free-tier deployment to Render
└── RUNBOOK.md                Operational reference
```

## Documentation map

| File | When to read it |
|---|---|
| [README.md](README.md) | Right now. Overview, setup, API surface. |
| [USAGE.md](USAGE.md) | First-time user / reviewer walkthrough. |
| [DOCKER.md](DOCKER.md) | Containerizing and pushing to Docker Hub via GitHub Actions. |
| [DEPLOY.md](DEPLOY.md) | Putting the app on a public HTTPS URL for free, long-term (Render + Clever Cloud MySQL). |
| [RUNBOOK.md](RUNBOOK.md) | Operational guide — diagnostics, backups, rollbacks, incident response. |
| [GITHUB_SETUP.md](GITHUB_SETUP.md) | One-time: pushing this code to a GitHub repo (Windows-flavored). |

## Running locally (without Docker)

### 1. Database

Make sure MySQL 8 is running locally. Create a user that can create databases
(or use root for dev). Then:

```bash
cd backend
cp .env.example .env
# Edit .env to match your MySQL credentials
```

### 2. Install + seed

```bash
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py                    # creates DB, schema, sample products & accounts
```

The seed creates two demo accounts:

| Role  | Email              | Password    |
|-------|--------------------|-------------|
| Admin | admin@jewel.com    | Admin@123   |
| User  | demo@jewel.com     | Demo@123    |

### 3. Run the app

```bash
python app.py
```

Then open **`http://localhost:5000`** in your browser. Flask serves both the
API (`/api/*`) and the static frontend (`/`, `/login.html`, `/admin.html`, …)
from the same origin — no separate static server needed, no CORS to configure.

> **Why same-origin?** Session cookies and `SameSite=Lax` work cleanly only
> when the frontend and API share an origin. Running the static files on a
> different port (e.g. `python -m http.server 8000`) is supported but requires
> setting `CORS_ORIGIN` in `backend/.env` to match exactly, *and* recent
> browsers may still drop the session cookie due to SameSite. **Stick with
> same-origin via `python app.py` unless you have a reason not to.**

#### Optional: serving the frontend separately

If you want to serve the static files yourself (e.g. live-reload tooling):

```bash
cd ../frontend
python -m http.server 8000
```

Then set `CORS_ORIGIN=http://localhost:8000` in `backend/.env` and restart
`python app.py`. Open `http://localhost:8000`.

## Running with Docker

```bash
docker compose up --build
```

The app (API + frontend, single container) is at `http://localhost:5000`.
MySQL is exposed on `:3306` for direct inspection.

After the containers come up the first time, seed the DB:

```bash
docker compose exec app python seed.py
```

For a full walkthrough — building, pushing to Docker Hub, and the GitHub
Actions CI/CD pipeline that automates it — see **[DOCKER.md](DOCKER.md)**.

The published image lives at
[`manasi2210/the-jewel-nest-studio`](https://hub.docker.com/r/manasi2210/the-jewel-nest-studio):

```bash
docker pull manasi2210/the-jewel-nest-studio:latest
```

## API surface

All endpoints are under `/api/`. Cookies (`credentials: include`) carry the session.

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

GET    /api/products            ?category=&min_price=&max_price=&search=&sort=&limit=&offset=
GET    /api/products/categories
GET    /api/products/:id

GET    /api/cart
POST   /api/cart/add            { product_id, quantity }
POST   /api/cart/update         { product_id, quantity }
POST   /api/cart/remove/:id
POST   /api/cart/clear

POST   /api/orders/checkout     { address, phone, payment_method }
GET    /api/orders

POST   /api/reviews             { product_id, rating, comment }
GET    /api/reviews/product/:id

# admin only
GET    /api/admin/stats
POST   /api/admin/products      (multipart for image upload, or JSON)
PUT    /api/admin/products/:id
DELETE /api/admin/products/:id
GET    /api/admin/orders
PUT    /api/admin/orders/:id/status
GET    /api/admin/users

POST   /api/admin/expenses
GET    /api/admin/expenses      ?month=&year=
DELETE /api/admin/expenses/:id
GET    /api/admin/expenses/dashboard?year=
```

## Database schema

See `backend/schema.sql`. Highlights:

- Foreign keys with appropriate `ON DELETE` (CASCADE for user-owned data,
  RESTRICT on `order_items.product_id` to preserve order history).
- Indexes on every foreign key plus `products(category, price)` and
  `orders(status)` for hot read paths.
- Unique constraint on `(user_id, product_id)` in `reviews` — one review
  per user per product.
- `CHECK` constraint enforces 1-5 rating range.
- FULLTEXT index on `products(name, description)` ready for richer search.

## Extending

- Drop in **Stripe / Razorpay** — implement a payment gateway in
  `services/payment_service.py`, call it before `OrderModel.create_with_items`.
- Convert to **JWT auth** — replace `Flask-Session` with a JWT in
  `routes/auth.py`; keep the decorators in `utils/decorators.py`.
- Move data layer to **SQLAlchemy** — every model exposes a small surface
  (`get`, `list`, `create`, `update`, `delete`); a swap is mechanical.

## License

MIT — use it, fork it, ship it.

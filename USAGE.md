# The Jewel Nest Studio — Usage Guide

A single guide covering three audiences:

1. **[Customers](#part-1--for-customers)** — how to use the store
2. **[Reviewers / Developers](#part-2--for-reviewers--developers)** — how to evaluate the project
3. **[Quick reference](#part-3--quick-reference-cheat-sheet)** — startup cheat-sheet for next time

If you're just here to log in, skip to **[Demo Accounts](#demo-accounts)**.

---

## Demo Accounts

The seed script creates two demo accounts. Use whichever matches what you want to do.

| Role         | Email             | Password   | What you can do                                |
|--------------|-------------------|------------|------------------------------------------------|
| **Admin**    | `admin@jewel.com` | `Admin@123`| Manage products, orders, expenses              |
| **Customer** | `demo@jewel.com`  | `Demo@123` | Browse, add to cart, checkout, leave reviews   |

You can also **register a fresh customer account** from the Register page.

---

## Part 1 — For Customers

### Starting the app

You need two things running at the same time:

1. **MySQL** — the Windows service `MySQL80` (started automatically on boot, or run `Start-Service MySQL80` in Admin PowerShell).
2. **Backend** (Flask) on port 5000 — this also serves the frontend at the same URL.

If a developer set this up for you, the app should already be running at `http://localhost:5000`. Otherwise jump to **[Part 3](#part-3--quick-reference-cheat-sheet)** for the start commands.

### The customer journey

#### 1. Browse the home page

Open `http://localhost:5000`. You'll see:

- A hero banner with featured jewelry imagery.
- A **"Our Categories"** grid (Rings, Necklaces, Earrings, Bracelets) — click any to filter the shop by that category.
- A **"Most Loved"** section showing top-rated products.
- A **"Follow our story"** section with links to our [Instagram](https://www.instagram.com/_the_jewelnest_studio__) and [YouTube](https://youtube.com/@jewelnest-v4h).

You don't need to be logged in to browse.

#### 2. Sign in or register

Click **Login** in the top-right corner.

- **Existing customer:** enter `demo@jewel.com` / `Demo@123`.
- **New customer:** click **"Create an account"** under the form. Fill in name, email, and a password (minimum 6 characters). You'll be logged in immediately after registering.

#### 3. Shop the collection

Click **Shop** in the top nav.

You can filter by:
- **Search** — matches name and description.
- **Category** — Rings / Necklaces / Earrings / Bracelets.
- **Price range** — set min and/or max.
- **Sort** — Newest, Price (low → high or high → low), or Top Rated.

Click any product card to view its detail page.

#### 4. Product details

The detail page shows the full image, description, material, stock status, average rating, and existing customer reviews.

- Use the **quantity selector** to choose how many to add.
- Click **Add to Cart**.
- A toast confirmation appears in the bottom-right.

If you're not logged in, "Add to Cart" sends you to the login page first.

#### 5. Leave a review

If logged in and viewing a product:

- Scroll to the **Reviews** section.
- Click stars to rate (1-5).
- Optionally write a comment.
- Click **Submit Review**.

You can only have one review per product — submitting again updates your previous one.

#### 6. Cart

Click the **Cart** link (top-right, with item count badge).

- Adjust quantities with the `+` / `-` buttons.
- Remove items with the `×` button.
- See the running total in the right-hand summary panel.
- Click **Checkout** when ready.

#### 7. Checkout

On the Checkout page:

- Enter a **delivery address** (any text, this is a demo).
- Enter a **phone number**.
- Pick a **payment method** — Cash on Delivery / Card / UPI.

> 💡 Payment is **simulated** — no charge is made, no payment gateway is called. The order is created in `pending` status.

Click **Place Order**. You're redirected to the Orders page with a success toast.

#### 8. Order history

Click **Orders** in the top nav. You'll see every order you've placed, including:

- Order number
- Status (`pending`, `processing`, `shipped`, `delivered`, `cancelled`) — colored badges.
- Items with quantities and unit prices.
- Delivery address and total.

Status updates whenever an admin changes it.

#### 9. Logout

Top-right corner, **Logout**. Your cart persists between sessions (it's stored server-side tied to your account).

---

## Part 2 — For Reviewers / Developers

This section is for someone who has the source code and wants to evaluate the application.

### Setup (first time)

See [`README.md`](README.md) for the full setup. The TL;DR:

```powershell
cd backend
cp .env.example .env       # edit DB_PASSWORD if your MySQL root differs
pip install -r requirements.txt
python seed.py             # creates DB, schema, sample data
python app.py              # serves API + frontend on http://localhost:5000
```

That's it — Flask serves both the API (`/api/*`) and the static frontend (`/`, `/login.html`, …) from the same origin, so there's nothing to configure for CORS or sessions.

> Want a separate static server (e.g. for live-reload)? Run `python -m http.server 8000` from `frontend/`, then set `CORS_ORIGIN=http://localhost:8000` in `backend/.env` and restart the API. Same-origin is simpler and avoids browser SameSite-cookie pitfalls — prefer it unless you specifically need a separate server.

### Logging in as Admin

1. Open `http://localhost:5000/login.html`.
2. Use `admin@jewel.com` / `Admin@123`.
3. After login, you're redirected to **`/admin.html`** automatically (because of the `admin` role).

The admin nav link only appears when you're logged in as an admin — so customers don't see it.

### Admin panel — what to test

The admin panel has four tabs (left sidebar). Test each:

#### Tab 1: Dashboard

- **KPIs** — Users, Products, Orders, Pending, Revenue.
- **Recent Orders table** — last 8 orders with customer info and status badges.

Loads on first open. Refresh by switching tabs and back.

#### Tab 2: Products

- **Add a product:** fill the form (name, category, price, stock are required). Optionally upload an image. Click **Save Product**.
- **Edit:** click `Edit` on any row. The form populates; edit and save.
- **Delete:** click `Delete` on any row. Confirms before deleting.
- **Image upload:** images are saved to `backend/uploads/` and served from `/uploads/<filename>`.

Try filtering on the **Shop** page after adding a product to confirm it appears.

#### Tab 3: Orders

Shows all orders across all customers.

- **Status dropdown** — change a status (`pending` → `processing` → `shipped` → `delivered`, or `cancelled`).
- Click **Save** to commit.
- Log in as the customer (`demo@jewel.com`) and visit Orders to verify the status changed.

#### Tab 4: Expenses

The store-internal expense tracker. Three things to verify:

- **Add an expense:** fill type, amount, date (defaults to today), optional note. Click **Add Expense**.
- **Monthly bar chart:** auto-renders for the selected year. Each bar shows the total and the month label. Hover for the exact value.
- **Delete an expense** from the table.

Switch the year dropdown to see prior years (the seed adds a few sample expenses to the current year).

### What to verify works end-to-end

- [ ] Register → login → browse → add to cart → checkout → see order in history.
- [ ] Stock decrements after checkout (try checking out an item, then verify the product detail shows lower stock).
- [ ] Cart enforces stock (try adding more than available — backend rejects it).
- [ ] Reviews — one per (user, product). Submit a second review for the same product → it updates the first.
- [ ] Admin sees the new order, updates status, customer sees the new status.
- [ ] Admin product CRUD reflects on the public Shop page immediately.
- [ ] Expense dashboard recalculates after adding/deleting.
- [ ] Logout clears session — visiting `/admin.html` after logout redirects to login.

### Architecture quick tour

| Layer       | File                                              | What it does                              |
|-------------|---------------------------------------------------|-------------------------------------------|
| Entry point | `backend/app.py`                                  | App factory, registers blueprints, error handlers |
| Auth        | `backend/routes/auth.py` + `services/auth_service.py` | Bcrypt + Flask-Session                |
| Data layer  | `backend/models/*.py`                             | Raw SQL, parameterized                    |
| Validation  | `backend/utils/validators.py`                     | Marshmallow schemas per endpoint          |
| Permissions | `backend/utils/decorators.py`                     | `@login_required`, `@admin_required`      |
| Schema      | `backend/schema.sql`                              | All tables, FKs, indexes                  |
| Frontend    | `frontend/js/api.js`                              | Central fetch client + UI helpers         |

### API surface

All API endpoints are listed in `README.md` under the **API surface** section. Hit `http://localhost:5000/api/health` to confirm the API is up.

---

## Part 3 — Quick Reference Cheat-Sheet

For when you come back to this project later and just need to remember how to start it.

### Start everything (Windows)

```powershell
# 1. Make sure MySQL service is running
Start-Service MySQL80          # ignore "already running" error if you see one

# 2. Start the app (one terminal — Flask serves API + frontend)
cd D:\application\backend
python app.py
```

Open `http://localhost:5000`.

### Stop everything

- Python process: `Ctrl+C` in its terminal.
- MySQL service (optional): `Stop-Service MySQL80` (Admin PowerShell).

### Demo logins

- Admin: `admin@jewel.com` / `Admin@123`
- Customer: `demo@jewel.com` / `Demo@123`

### Reset the database

If you've messed up data and want to start fresh:

```powershell
cd D:\application\backend
python seed.py
```

The seed is **idempotent for users** (won't overwrite admin/demo passwords) but **only seeds products and expenses if the tables are empty**. To force a full reset, drop the database first:

```powershell
mysql -u root -proot -e "DROP DATABASE jewelry_store;"
python seed.py
```

### Common issues

| Symptom | Cause | Fix |
|---|---|---|
| API logs `Access denied for user 'root'` | `DB_PASSWORD` in `.env` doesn't match MySQL | Update `.env` and restart `python app.py` |
| Login appears to succeed but every subsequent page says "Authentication required" | You're serving the frontend on a different origin than the API and the browser is dropping the `SameSite=Lax` session cookie | Switch to same-origin: open the app at `http://localhost:5000` (served by Flask itself) instead of running a separate static server |
| Login button does nothing / browser console shows a CORS error | You're serving the frontend separately and `CORS_ORIGIN` in `backend/.env` doesn't match the frontend URL exactly | Either set `CORS_ORIGIN=http://localhost:8000` (or whatever your frontend URL is) and restart the API, or switch to same-origin (`http://localhost:5000`) |
| Browser shows a blank page or 404 at `/login.html` | The frontend folder isn't where Flask expects | Make sure `frontend/` sits next to `backend/` in the project root — `app.py` resolves it relative to itself |
| `mysql.connector.errors.ProgrammingError: 1045` | Wrong DB password | Same as the first row |
| Admin nav link doesn't appear after login | You logged in as the demo customer, not admin | Log out, log in as `admin@jewel.com` |
| "Out of stock" toast on Add to Cart | Product stock is 0 (other tests depleted it) | Use admin to bump the stock value |

### Where things live

```
D:\application\
├── backend\
│   ├── .env              ← DB password lives here
│   ├── app.py            ← run this (API on :5000)
│   ├── seed.py           ← run this to (re)seed
│   ├── uploads\          ← admin-uploaded product images
│   └── logs\app.log      ← rotating log file
└── frontend\
    └── (HTML/CSS/JS — serve with python http.server)
```

---

## What this guide doesn't cover

- **Production deployment** — see `README.md` for Docker setup. Beyond that, you'd want a real WSGI server (gunicorn behind nginx), HTTPS, a stronger SECRET_KEY, and a managed MySQL.
- **Customizing the design** — edit `frontend/css/style.css` (variables at the top in `:root`).
- **Adding a payment provider** — sketch in `README.md` under "Extending".

If something here is wrong or unclear, the best signal is "the page isn't doing what the guide promises" — open browser DevTools (F12) → Network tab → check what the failing API call actually returns. That's almost always the first clue.

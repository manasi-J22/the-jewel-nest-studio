# Deploying for free, long-term

A practical setup for a low-traffic site (1–2 visitors). Genuinely free, no expirations, no credit card required for either service.

You'll end up with:

- A live app at `https://the-jewel-nest-studio.onrender.com`, HTTPS automatic.
- A managed MySQL database on Clever Cloud's permanent free 256 MB plan.
- Auto-deploy: when GitHub Actions pushes a new image to Docker Hub, Render redeploys.

**Total cost: $0 forever** for low traffic.
**Total time: ~25 minutes.**

> **Why two platforms?** Render gives you a free Web Service that pulls Docker Hub images directly, but doesn't offer free MySQL (only Postgres). Clever Cloud gives you free MySQL with no card. Pairing them is the only fully-free, no-expiration, no-card path that doesn't require code changes.

> **The one trade-off:** Render's free Web Service spins down after 15 minutes of inactivity. The next request takes ~30 seconds to wake it. After that, fast again. For 1–2 visitors this is fine — and there are workarounds at the bottom of this guide if it bothers you.

---

## Prerequisites

- Code pushed to GitHub.
- The Docker image at `manasi2210/the-jewel-nest-studio:latest` on Docker Hub. Verify: https://hub.docker.com/r/manasi2210/the-jewel-nest-studio. (Your CI/CD already pushes this on every `main` push.)
- A GitHub account (you'll use it to sign into Render).
- ~25 minutes.

You'll create two accounts during this guide. Both free, no card:

- **Clever Cloud** (https://www.clever-cloud.com) — for free MySQL
- **Render** (https://render.com) — for the free web service

---

## Part 1 — Free MySQL on Clever Cloud

### 1.1 — Sign up

1. Go to https://www.clever-cloud.com.
2. The site might load in French — there's a language toggle at the top-right (look for a flag icon or "EN").
3. Click **Sign up** → use email or sign in with GitHub. Verify your email.
4. On first login you'll land on the **Console**. Clever Cloud may ask you to create an "organization" — name it `personal` or anything you like.

### 1.2 — Create the MySQL add-on

1. Console → left sidebar → **Create…** → **an add-on**.
2. Choose **MySQL**.
3. **Plan:** select **DEV** — it's the free tier. You'll see "Free, 10 connections, 256 MB". Confirm "DEV" is highlighted.
4. **Region:** any (Paris is closest to Render's EU regions; Montréal is closest to US-East). Pick whichever matches the Render region you'll choose in Part 2.
5. **Name:** `jewel-mysql`.
6. Click **Next** → **Create**.

The DB provisions in ~30 seconds.

### 1.3 — Grab the connection details

1. From the Console, open the `jewel-mysql` add-on.
2. Open the **Information** tab. You'll see a card listing:
   - **`MYSQL_ADDON_HOST`** — something like `bxxx-mysql.services.clever-cloud.com`
   - **`MYSQL_ADDON_PORT`** — usually `3306` but sometimes randomized
   - **`MYSQL_ADDON_USER`** — auto-generated, looks like `unxxxxxxxxx`
   - **`MYSQL_ADDON_PASSWORD`** — click the eye icon to reveal
   - **`MYSQL_ADDON_DB`** — auto-generated DB name, looks like `bxxx`

3. Copy all five into a scratch file — you'll need them in Part 2.4 and Part 3.

> The auto-generated DB name (e.g. `bxxxxxxxxxx`) is what we'll use as `DB_NAME`. Clever Cloud's free MySQL doesn't let you create additional databases — you only get the one. Our app respects whatever DB name you give it via `DB_NAME`, so this is fine.

### 1.4 — Test the connection from your laptop

```bash
mysql -h <MYSQL_ADDON_HOST> -P <MYSQL_ADDON_PORT> \
      -u <MYSQL_ADDON_USER> -p<MYSQL_ADDON_PASSWORD> \
      <MYSQL_ADDON_DB> \
      -e "SELECT 'Hello from Clever Cloud' AS message;"
```

If you don't have `mysql` installed locally, skip this — the Render deploy in Part 2 will tell you if the connection works.

---

## Part 2 — Free web service on Render

### 2.1 — Sign up

1. Go to https://render.com → **Get Started**.
2. Sign up with GitHub (easiest — it sets up the auto-deploy webhook later).
3. Skip any "Add a credit card" prompts — the Free plan doesn't require one.

### 2.2 — Create a Web Service from the Docker Hub image

1. Render dashboard → **+ New** → **Web Service**.
2. On the source picker page, choose **Existing Image** (sometimes labeled "Deploy an existing image from a registry").
3. **Image URL:** `docker.io/manasi2210/the-jewel-nest-studio:latest`
4. Leave Docker Hub credentials blank (the image is public).
5. Click **Connect** → **Next**.

### 2.3 — Configure the service

| Field | Value |
|---|---|
| **Name** | `the-jewel-nest-studio` (your URL becomes `the-jewel-nest-studio.onrender.com`) |
| **Region** | Same region you picked for Clever Cloud (e.g. Frankfurt for Paris, Ohio for Montréal) |
| **Instance Type** | **Free** |

Scroll down to **Advanced** → **Add Environment Variable** for each row in the next section.

### 2.4 — Add environment variables

| Key | Value |
|---|---|
| `DB_HOST` | `MYSQL_ADDON_HOST` from Clever Cloud (Part 1.3) |
| `DB_PORT` | `MYSQL_ADDON_PORT` from Clever Cloud |
| `DB_USER` | `MYSQL_ADDON_USER` from Clever Cloud |
| `DB_PASSWORD` | `MYSQL_ADDON_PASSWORD` from Clever Cloud |
| `DB_NAME` | `MYSQL_ADDON_DB` from Clever Cloud (the auto-generated `bxxx...` name) |
| `SECRET_KEY` | Run `openssl rand -hex 32` locally and paste the output |
| `FLASK_ENV` | `production` |
| `WEB_CONCURRENCY` | `1` (free tier has 512 MB RAM; one worker fits comfortably) |
| `PORT` | `5000` |

> 🔐 `DB_PASSWORD` and `SECRET_KEY` are secrets. Render encrypts them at rest, masks them in the UI, and only injects them into your container at runtime.

Important: also confirm Render is routing traffic to **port 5000**. There's a separate **Port** field near the top of the form — set it to `5000` if it's not auto-detected.

### 2.5 — Deploy

Click **Create Web Service** at the bottom.

Render pulls the image (~30 s) and starts the container. The **Logs** panel auto-opens. You should see:

```
[INFO] Listening at: http://0.0.0.0:5000 (1)
[INFO] Booting worker with pid: ...
DB connection pool initialized
```

If `DB connection pool initialized` is missing or you see an error like `Can't connect to MySQL server`:
- Re-check the env vars in Settings → Environment.
- Confirm Clever Cloud isn't blocking Render's IP. Clever Cloud's free MySQL doesn't have IP allowlisting by default, so this should "just work".

When the status badge turns green ("Live"), open the URL Render shows you.

### 2.6 — Seed the database

The app is up but the database is empty — the first login will fail with "Invalid credentials" because there are no users yet.

Render's free tier no longer includes a Shell tab, so we run `seed.py` locally pointed at Clever Cloud's MySQL.

From your laptop:

```bash
cd /home/ttpl-lnv-0042/Downloads/the-jewel-nest-studio/backend

# (if you haven't already)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

DB_HOST=<MYSQL_ADDON_HOST> \
DB_PORT=<MYSQL_ADDON_PORT> \
DB_USER=<MYSQL_ADDON_USER> \
DB_PASSWORD=<MYSQL_ADDON_PASSWORD> \
DB_NAME=<MYSQL_ADDON_DB> \
python3 seed.py
```

You should see:

```
Connecting to MySQL at <host>:<port>…
Applying schema…
Seeding admin and demo users…
Seeding products…
Seeding sample expenses…

✓ Seed complete.
  Admin login:  admin@jewel.com / Admin@123
  User login:   demo@jewel.com  / Demo@123
```

> The seed script auto-detects "user can't create databases" (Clever Cloud's free MySQL doesn't grant `CREATE DATABASE` to its DB users) and prints `(skipping CREATE DATABASE: …) — using existing DB <name>` before continuing. As long as `DB_NAME` points at the auto-provisioned `bxxx...` database, the schema will apply against it correctly.

### 2.7 — Verify the deployment

```bash
curl -fsS https://your-app.onrender.com/api/health
# → {"status":"ok"}
```

If you got that, open the URL in a browser, click **Login**, sign in as `admin@jewel.com` / `Admin@123`. You should land on the admin panel.

🎉 **You're live.**

---

## Part 3 — Auto-deploy from Docker Hub

Right now Render won't redeploy when your CI pushes a new image to Docker Hub. Two ways to fix that:

### Option A (simplest) — Render's image polling

Render's Free plan polls Docker Hub for `:latest` automatically every few minutes. It already works. No setup. Slight lag (3–10 min between Docker Hub push and Render redeploy).

### Option B (instant) — Deploy webhook + GitHub Actions

If you want the redeploy to fire **immediately** after Docker Hub push:

1. **Get the Render deploy hook:**
   - Render dashboard → service → **Settings** → scroll to **Deploy Hook**.
   - Copy the URL — looks like `https://api.render.com/deploy/srv-xxx?key=yyy`.

2. **Add it as a GitHub secret:**
   - GitHub repo → **Settings** → **Secrets and variables** → **Actions**.
   - **New repository secret**:
     - **Name:** `RENDER_DEPLOY_HOOK`
     - **Value:** the URL from step 1.

3. **Add a step to the release workflow.** Edit `.github/workflows/release.yml`. After the "Build and push" step, before "Image summary":

   ```yaml
         - name: Trigger Render redeploy
           if: github.ref == 'refs/heads/main'
           run: curl -fsS -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
   ```

   Commit and push.

Now the flow is:

```
git push origin main
  → GitHub Actions: Release workflow runs
    → Builds + pushes manasi2210/the-jewel-nest-studio:latest to Docker Hub
    → POSTs to RENDER_DEPLOY_HOOK
      → Render pulls the new :latest image and redeploys (~1–2 minutes)
```

---

## Part 4 — Custom domain (optional)

If you own a domain (e.g. `jewelnest.studio`):

1. Render dashboard → service → **Settings** → **Custom Domains** → **Add Custom Domain**.
2. Enter `jewelnest.studio` (and/or `www.jewelnest.studio`).
3. Render shows a CNAME (or A record at the apex). Add it at your DNS provider.
4. Wait 5–30 min for DNS propagation.
5. Render auto-provisions a Let's Encrypt cert. Done.

---

## Operational notes (free tiers in detail)

### Render Free Web Service

| Behavior | Detail |
|---|---|
| **Sleep after inactivity** | Container stops after 15 min of no incoming requests. Next request takes ~30s to wake. |
| **Bandwidth** | 100 GB/month outbound — far more than you need for 1–2 visitors. |
| **Memory** | 512 MB. With `WEB_CONCURRENCY=1` you have plenty of headroom. |
| **Disk** | Ephemeral. Anything written to the container's filesystem is **lost on restart/redeploy**. The DB is on Clever Cloud so this only matters for uploaded product images. |
| **Logs** | 7-day retention. Stream live in dashboard or download. |
| **Build minutes** | N/A — we're pulling a pre-built Docker image. |

### Clever Cloud Free MySQL

| Behavior | Detail |
|---|---|
| **Storage** | 256 MB. This app uses ~5 MB seeded — you have ~50× headroom. |
| **Connections** | 10 simultaneous. With one Render worker you'll use 1–3 typically. |
| **Backups** | None on the free plan. Back up manually with `mysqldump` (see RUNBOOK). |
| **Idle timeout** | The server closes idle connections; the app's connection pool reconnects automatically. First request after wake-up may be slightly slower. |
| **Region** | Once chosen, can't be changed. Don't worry — pick anything. |

### What you can't do on this stack

- **Persist admin-uploaded product images.** Render Free has no persistent disk. If an admin uploads images, they'll vanish on the next redeploy. **Workaround:** the seeded products all use external `image_url`s (Unsplash). Tell admins to paste image URLs instead of uploading. Or migrate to Cloudflare R2 (10 GB free) when you need real uploads.
- **Run database migrations automatically on deploy.** No shell access on Free. Run them locally with `mysql -h <host> ... < migration.sql`.

### Working around the cold start

For 1–2 visitors per day a 30s wait once is fine. If it bothers you:

- **UptimeRobot** (free): pings `/api/health` every 5 minutes from outside, keeping the container warm. Slightly against Render's spirit-of-the-rules; widely used. https://uptimerobot.com
- **Upgrade to Render Starter** ($7/mo): always-on, persistent disk, more RAM. Worth it only if traffic grows.

---

## Backup the database

Free Clever Cloud has no managed backups, so do it yourself. Once a week is generous for low-traffic data.

```bash
mysqldump -h <MYSQL_ADDON_HOST> -P <MYSQL_ADDON_PORT> \
          -u <MYSQL_ADDON_USER> -p<MYSQL_ADDON_PASSWORD> \
          <MYSQL_ADDON_DB> \
          > jewel-backup-$(date +%Y%m%d).sql
```

To restore (destructive — wipes existing tables):

```bash
mysql -h <host> -P <port> -u <user> -p<pw> <db> < jewel-backup-20260510.sql
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Render build fails: "pull access denied" | Image is private on Docker Hub | hub.docker.com → repo → Settings → Make Public; or add Docker Hub credentials in Render |
| Render shows "Live" but URL returns 502 | App crashed on boot | Render → service → **Logs** → look for the first error. Almost always: wrong DB env var |
| `Can't connect to MySQL server` in logs | Wrong DB host/port/user/password/db | Re-check each env var matches Clever Cloud's Information tab character-for-character. The user is `unxxxxxxxxx`, not `root` |
| `1044 (42000): Access denied …` during seed but the script keeps going | Expected on Clever Cloud — the script skips `CREATE DATABASE` and uses the pre-provisioned DB | None. This is normal; the seed should still complete successfully |
| `Invalid credentials` on first login | DB has schema but no users — seed didn't complete | Re-run Part 2.6 |
| URL takes 30 seconds to load the first time | Render free tier cold start | Expected. Subsequent requests are fast. See "Working around the cold start" above |
| Auto-deploy doesn't fire | Webhook not wired up (Part 3 Option B) | Either add the webhook step, or wait 3–10 min for Render's polling to detect the new image |
| Image uploaded by admin disappears after a few days | Render Free has no persistent disk | Tell admins to use image URLs; or upgrade to Starter for $7/mo persistent disk; or wire up Cloudflare R2 |
| Clever Cloud says "256 MB exceeded" | DB has filled up (very unlikely for this app) | Delete old order rows, or run `OPTIMIZE TABLE` on every table to reclaim space |

---

## Quick reference

```bash
# Verify image is on Docker Hub
docker pull manasi2210/the-jewel-nest-studio:latest

# Health-check your live deployment
curl https://your-app.onrender.com/api/health

# Seed the DB (one-time, from your laptop, with Clever Cloud creds)
cd backend
DB_HOST=<host> DB_PORT=<port> DB_USER=<user> \
DB_PASSWORD=<pw> DB_NAME=<db> \
python3 seed.py

# Backup
mysqldump -h <host> -P <port> -u <user> -p<pw> <db> > backup-$(date +%F).sql

# Trigger a manual redeploy (alternative to git push)
curl -X POST "<RENDER_DEPLOY_HOOK>"

# Tail logs
# Render dashboard → service → Logs tab
```

---

## When you outgrow this

You won't, given 1–2 visitors. But for reference, the cheapest jumps:

| Limit hit | Upgrade | Cost |
|---|---|---|
| Cold start matters | Render Starter | $7/mo |
| 256 MB DB exceeded | Clever Cloud upgrade or migrate to PlanetScale Hobby | $7–15/mo |
| Image uploads need to persist | Add Cloudflare R2 (free 10 GB) | $0 |
| Real backups needed | Clever Cloud's paid plans include them | included with paid DB |

The migration from "free" to "paid" is just clicking "upgrade plan" — no code changes, same image, same env vars.

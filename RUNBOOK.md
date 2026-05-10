# Runbook

Operational reference for The Jewel Nest Studio. Use this when something is broken, when you need to perform a routine task, or when you need to look up where things live.

This is **not** a setup guide — see [README.md](README.md) for first-time setup, [USAGE.md](USAGE.md) for the user-facing walkthrough, and [DOCKER.md](DOCKER.md) for containerization. The runbook assumes the app is already deployed somewhere.

---

## Table of contents

- [Service inventory](#service-inventory)
- [Routine tasks](#routine-tasks)
- [Diagnostics](#diagnostics)
- [Incident response](#incident-response)
- [Backup & restore](#backup--restore)
- [Releases](#releases)
- [Rotating secrets](#rotating-secrets)
- [Emergency commands](#emergency-commands)

---

## Service inventory

| Component | What it is | Where it lives |
|---|---|---|
| **App container** | Flask + gunicorn, serves API and static frontend on `:5000` | `manasi2210/the-jewel-nest-studio:latest` on Docker Hub |
| **Database** | MySQL 8 with the `jewelry_store` schema | Compose: `db` service. Production: external (Aiven / managed MySQL) |
| **Sessions** | Server-side, stored on disk via Flask-Session | Volume `sessions` mounted at `/app/flask_session` |
| **Uploaded images** | Admin-uploaded product images served via `/uploads/<file>` | Volume `uploads` mounted at `/app/uploads` |
| **Logs** | Rotating file logs (2MB × 5) + stdout | Volume `logs` mounted at `/app/logs/app.log`. Always also on stdout. |
| **CI** | Lint + smoke test on every push/PR | `.github/workflows/ci.yml` |
| **Release pipeline** | Multi-arch image push to Docker Hub | `.github/workflows/release.yml` |

### Endpoints

| Path | Purpose | Auth |
|---|---|---|
| `GET /api/health` | Liveness probe | none |
| `POST /api/auth/login` | Sign in | none (public) |
| `POST /api/auth/logout` | Sign out | session |
| `GET /api/auth/me` | Current user | session |
| `GET /api/products` | Public catalog | none |
| `GET /api/cart` / `POST /api/cart/...` | Cart ops | session |
| `POST /api/orders/checkout` | Checkout | session |
| `POST /api/admin/...` | Admin operations | admin role |
| `/` and `/*.html`, `/css/...`, `/js/...` | Static frontend | none |

Full list in [README.md](README.md#api-surface).

---

## Routine tasks

### Restart the app (no data loss)

```bash
# Local / VM with compose
docker compose restart app

# Render
# Dashboard → service → "Manual Deploy" → "Restart Service"
```

Sessions survive (named volume). DB unaffected.

### Deploy a new version

You don't deploy by uploading code. You deploy by pushing to `main` (or tagging a release):

```bash
git push origin main         # triggers .github/workflows/release.yml
# → image manasi2210/the-jewel-nest-studio:latest is rebuilt and pushed
```

For a versioned release:

```bash
git tag v0.2.0
git push origin v0.2.0       # produces tags v0.2.0, 0.2.0, 0.2 on Docker Hub
```

Then on the host running the image, pull and restart:

```bash
docker compose pull app
docker compose up -d app
```

On Render: the service auto-redeploys when the Docker Hub tag updates if you've enabled the webhook (see [DEPLOY.md](DEPLOY.md)).

### Reset the database to a clean seed

```bash
docker compose down -v       # destroys ALL volumes including DB and uploads
docker compose up -d
docker compose exec app python seed.py
```

⚠️ This wipes uploaded images and sessions too. For a DB-only reset:

```bash
docker compose exec db mysql -uroot -proot -e "DROP DATABASE jewelry_store; CREATE DATABASE jewelry_store;"
docker compose exec app python seed.py
```

### Add an admin user manually

```bash
docker compose exec app python -c "
from services.auth_service import AuthService
from models.user import UserModel
user_id = UserModel.create('Jane Admin', 'jane@example.com',
                            AuthService.hash_password('NewPass@123'),
                            phone=None, role='admin')
print('Created admin id', user_id)
"
```

### Tail logs

```bash
docker compose logs -f app           # app logs (gunicorn + Flask)
docker compose logs -f db            # MySQL logs
docker compose logs --tail=200 app   # last 200 lines

# Render: dashboard → service → "Logs" tab (live tail)
```

Logs are also written to `/app/logs/app.log` inside the container. Pull the file with:

```bash
docker compose cp app:/app/logs/app.log ./app.log
```

---

## Diagnostics

### App is unreachable (connection refused)

```bash
docker compose ps
# State should be "Up" and "healthy"
```

If the state is `Restarting`:

```bash
docker compose logs --tail=100 app
```

Look for the **first** error. Common ones:
- `Can't connect to MySQL` → DB isn't up or `DB_HOST` is wrong
- `PermissionError: '/app/logs/...'` → bind-mount permission mismatch (use named volumes — fixed in current `docker-compose.yml`)
- `Address already in use` → port 5000 conflict on the host

### Login fails with "Invalid credentials"

Most common: DB never seeded.

```bash
docker compose exec app python seed.py
```

If seeded but still failing, check the user actually exists:

```bash
docker compose exec db mysql -uroot -proot jewelry_store -e \
  "SELECT id, email, role FROM users;"
```

### Login succeeds but next page says "Authentication required"

This means the session cookie isn't being attached on the second request.

- Check that you're hitting the same origin both times (e.g. `http://localhost:5000` for both, not switching to `127.0.0.1` after login).
- Check `SESSION_COOKIE_SECURE` in [config.py](backend/config.py) — if `True`, cookies are sent only over HTTPS. In local dev it must be `False`.
- Browser DevTools → Application → Cookies → see if `session` is present for the origin.

### Image upload fails / 500 error

- Check `MAX_CONTENT_LENGTH` in `config.py` (default 8MB).
- Check upload directory is writable: `docker compose exec app ls -la /app/uploads`.
- Check disk space on the host: `docker system df`.

### MySQL out of disk

```bash
docker compose exec db mysql -uroot -proot -e \
  "SELECT table_schema, ROUND(SUM(data_length+index_length)/1024/1024, 2) AS size_mb
   FROM information_schema.tables GROUP BY table_schema;"
```

If `flask_session` files are filling the volume, expire old sessions:

```bash
docker compose exec app find /app/flask_session -mtime +30 -delete
```

---

## Incident response

### "The site is down"

1. **Confirm it's down** from outside your machine: `curl -fsS https://your-domain/api/health`
2. **Check container status** on the host: `docker compose ps`
3. **Check logs** for the last 200 lines: `docker compose logs --tail=200 app`
4. **Try a restart** as the cheapest fix: `docker compose restart app`
5. **If MySQL is the problem,** restart it next: `docker compose restart db && sleep 10 && docker compose restart app`
6. **If still down,** roll back to the previous image (see "Rollback" below).

### Rollback to the previous image

Every push to `main` produces a `sha-<short>` tag on Docker Hub in addition to `latest`. To roll back:

```bash
# Find a known-good tag from Docker Hub:
# https://hub.docker.com/r/manasi2210/the-jewel-nest-studio/tags

# Pull that specific tag
docker pull manasi2210/the-jewel-nest-studio:sha-abc1234

# Edit docker-compose.yml and change the image: line to that tag,
# then:
docker compose up -d app
```

Or with explicit override (no file edit):

```bash
IMAGE_TAG=sha-abc1234 docker compose up -d app
```

(Requires changing the compose `image:` line to `manasi2210/the-jewel-nest-studio:${IMAGE_TAG:-latest}`.)

### Database corruption / accidental wipe

See [Backup & restore](#backup--restore). If you didn't have a backup, the only recovery is to re-seed (loses all real data and re-creates the demo data).

### Suspected security breach

1. **Rotate `SECRET_KEY` immediately** (this invalidates every active session).
   - Generate: `openssl rand -hex 32`
   - Set new value in env / Render dashboard / `.env`
   - Restart the app
2. **Force admin password reset** by manually resetting in the DB:
   ```sql
   UPDATE users SET password_hash = '<bcrypt of new password>'
   WHERE email = 'admin@jewel.com';
   ```
3. **Rotate Docker Hub access token** (Docker Hub → Account → Personal access tokens → Revoke).
4. **Rotate DB password** if you suspect it leaked, and update everywhere it's referenced.
5. **Audit recent admin actions** — check `orders`, `users`, `expenses` for unexpected entries.

---

## Backup & restore

### Backup the database (compose)

```bash
docker compose exec -T db mysqldump -uroot -proot jewelry_store \
  > backup-$(date +%Y%m%d-%H%M).sql
```

### Backup uploaded images

```bash
docker compose cp app:/app/uploads ./uploads-backup-$(date +%Y%m%d)
```

### Restore the database

```bash
# Drop and recreate (destructive!)
docker compose exec -T db mysql -uroot -proot \
  -e "DROP DATABASE IF EXISTS jewelry_store; CREATE DATABASE jewelry_store;"

# Reload from backup
docker compose exec -T db mysql -uroot -proot jewelry_store < backup-20260509-1234.sql
```

### Restore uploaded images

```bash
docker compose cp ./uploads-backup-20260509 app:/app/uploads
```

### Recommended cadence

- **DB backup:** daily for prod, weekly for staging. Store off-host.
- **Uploads backup:** weekly, or any time after bulk image uploads.
- **Test the restore process** at least once before you need it.

---

## Releases

### Versioning

We use SemVer-flavored tags: `v<major>.<minor>.<patch>`.

- **Patch** (`v0.1.1`): bug fixes, no schema or API changes
- **Minor** (`v0.2.0`): new features, backwards-compatible
- **Major** (`v1.0.0`): breaking API changes, schema migrations needed

### Cutting a release

1. Make sure `main` is green (CI passing).
2. Update README/USAGE if the user-visible behavior changed.
3. Tag and push:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. Watch the Release workflow: GitHub → Actions tab.
5. Verify the tag landed: `docker pull manasi2210/the-jewel-nest-studio:v0.2.0`
6. Roll out to deploys (Render auto-pulls `latest`; for explicit version pinning, update the deployment config).

### Schema migrations

There's no migration framework yet. For now:

1. Edit `backend/schema.sql` for the new schema.
2. Write a one-off migration SQL script in the PR description.
3. After deploy, run it:
   ```bash
   docker compose exec -T db mysql -uroot -proot jewelry_store < migration.sql
   ```

For non-trivial schema changes, prefer adding columns over renaming, and never drop columns in the same release that adds the replacement — drop them one release later, after you've confirmed nothing reads them.

---

## Rotating secrets

### `SECRET_KEY` (Flask session signer)

- Why: invalidates all sessions; users must log in again.
- When: routinely (every 6 months) or immediately on any suspected leak.
- How: generate `openssl rand -hex 32`, update the env var on the host / Render, restart the app.

### Docker Hub access token

- Why: pushes images to your account.
- When: every 90 days (matches the GitHub Actions expectation), or on suspected leak.
- How: hub.docker.com → Account → Personal access tokens → Generate → update GitHub secret `DOCKERHUB_TOKEN`.

### MySQL password

- Why: protects the data.
- How: in the running DB, `ALTER USER 'root'@'%' IDENTIFIED BY 'newpw';` then update the env var the app uses (`DB_PASSWORD`) and restart the app.

---

## Emergency commands

Stop everything (data preserved):

```bash
docker compose down
```

Stop and **destroy all data** (DB, uploads, sessions, logs):

```bash
docker compose down -v
```

Force-rebuild the image and restart:

```bash
docker compose up --build -d
```

Connect a `bash` shell inside the running app container:

```bash
docker compose exec app bash
```

Connect to the MySQL prompt:

```bash
docker compose exec db mysql -uroot -proot jewelry_store
```

Inspect a container's environment:

```bash
docker compose exec app env | sort
```

Hard-stop a wedged container:

```bash
docker kill the-jewel-nest-studio-app-1
```

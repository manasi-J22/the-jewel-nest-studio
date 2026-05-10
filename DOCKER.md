# Containerization & CI/CD — step by step

This guide takes you from "code on a laptop" to "image on Docker Hub, built automatically by GitHub Actions". Follow it in order; each part stands on its own once the previous is done.

- **[Part 1 — What you've got](#part-1--what-youve-got)** — files added and what they do
- **[Part 2 — Build and run locally](#part-2--build-and-run-locally)** — verify the image works on your machine
- **[Part 3 — Push to Docker Hub manually](#part-3--push-to-docker-hub-manually)** — one-time, by hand
- **[Part 4 — CI/CD with GitHub Actions](#part-4--cicd-with-github-actions)** — automate everything on git push
- **[Part 5 — Deploying the published image](#part-5--deploying-the-published-image)** — anyone can pull and run it
- **[Troubleshooting](#troubleshooting)**

> All commands assume Docker Hub username `manasi2210`. If yours differs, swap it in. The image name is `manasi2210/the-jewel-nest-studio`.

---

## Part 1 — What you've got

These files were added/updated to make this work:

| File | Purpose |
|---|---|
| [Dockerfile](Dockerfile) | Bakes backend + frontend into one image |
| [.dockerignore](.dockerignore) | Keeps secrets, caches, and runtime state out of the image |
| [docker-compose.yml](docker-compose.yml) | One-command local stack: MySQL + the app on `:5000` |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Lint + smoke test on every push and PR |
| [.github/workflows/release.yml](.github/workflows/release.yml) | Build + push multi-arch image to Docker Hub on `main` and tags |

The published image runs **everything in one container**: gunicorn serves the API on `/api/*` and the static frontend on `/`. Same origin → no CORS, no SameSite cookie issues.

---

## Part 2 — Build and run locally

### 2a. Build the image

From the repo root (the directory with the top-level `Dockerfile`):

```bash
docker build -t manasi2210/the-jewel-nest-studio:dev .
```

First build pulls the Python base image and installs deps — expect a couple of minutes. Subsequent builds are seconds thanks to layer caching.

Verify:

```bash
docker images | grep the-jewel-nest-studio
```

### 2b. Run with docker-compose (recommended for local dev)

This brings up MySQL and the app together:

```bash
docker compose up --build
```

Wait until you see `Listening at: http://0.0.0.0:5000` from the `app` service.

In another terminal, seed the database (first time only):

```bash
docker compose exec app python seed.py
```

Open **http://localhost:5000** and log in with `admin@jewel.com` / `Admin@123`.

To stop:

```bash
docker compose down            # stops containers, keeps the DB volume
docker compose down -v         # also wipes the DB volume — fresh start
```

### 2c. Run the image standalone (without compose)

If you've already got MySQL running somewhere:

```bash
docker run --rm -p 5000:5000 \
  -e DB_HOST=host.docker.internal \
  -e DB_USER=root \
  -e DB_PASSWORD=root \
  -e DB_NAME=jewelry_store \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  manasi2210/the-jewel-nest-studio:dev
```

(`host.docker.internal` resolves to the host machine's IP from inside the container on Docker Desktop and recent Linux versions. On older Linux Docker, use `--network=host` and `DB_HOST=127.0.0.1` instead.)

---

## Part 3 — Push to Docker Hub manually

Do this once by hand to confirm it works. After that, [Part 4](#part-4--cicd-with-github-actions) automates it.

### 3a. Create a Docker Hub account and access token

1. Sign up / log in at https://hub.docker.com.
2. Click your avatar (top right) → **Account Settings** → **Personal access tokens** → **Generate new token**.
3. Name it `the-jewel-nest-studio-ci`, permissions: **Read, Write, Delete**.
4. **Copy the token now** — Docker Hub only shows it once. Looks like `dckr_pat_…`.

> 🔐 Treat this token like a password. Don't paste it into chats, screenshots, or commits.

### 3b. Log in from your terminal

```bash
echo "PASTE_YOUR_TOKEN_HERE" | docker login -u manasi2210 --password-stdin
```

You should see `Login Succeeded`. The token is stored in `~/.docker/config.json` so future pushes don't reprompt.

### 3c. Tag and push

```bash
# (Re)build with the canonical tag
docker build -t manasi2210/the-jewel-nest-studio:latest .

# Optionally also tag with a version
docker tag manasi2210/the-jewel-nest-studio:latest \
           manasi2210/the-jewel-nest-studio:v0.1.0

docker push manasi2210/the-jewel-nest-studio:latest
docker push manasi2210/the-jewel-nest-studio:v0.1.0
```

After it completes, refresh https://hub.docker.com/r/manasi2210/the-jewel-nest-studio — you should see both tags.

### 3d. Make the repository public (optional)

Docker Hub makes new repos private by default. If you want anyone to be able to `docker pull` without logging in:

1. Open your repo page on Docker Hub → **Settings** → **Visibility settings** → **Make Public**.

---

## Part 4 — CI/CD with GitHub Actions

Two workflows are wired up:

- **`ci.yml`** — runs on every push to `main` and every PR. Lints with `ruff`, spins up MySQL, runs `seed.py`, boots Flask, and verifies that `/api/health` responds AND that login works with the seeded admin. Also builds the Docker image (no push) so you catch broken Dockerfiles early.
- **`release.yml`** — runs on push to `main` and on git tags `v*.*.*`. Builds a multi-arch image (`linux/amd64,linux/arm64`) and pushes it to Docker Hub with intelligent tags.

### 4a. Add Docker Hub secrets to your GitHub repo

GitHub Actions needs your Docker Hub credentials to push.

1. On GitHub, open your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Add **two** secrets:

| Name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | `manasi2210` |
| `DOCKERHUB_TOKEN` | the access token from [step 3a](#3a-create-a-docker-hub-account-and-access-token) (paste the `dckr_pat_…` value) |

> Don't put these in `.env`, in code, or in commit messages. GitHub encrypts secrets at rest and only exposes them to workflow runs.

### 4b. Push the workflows to GitHub

If you haven't yet:

```bash
cd /path/to/the-jewel-nest-studio
git add .github Dockerfile .dockerignore docker-compose.yml DOCKER.md
git commit -m "ci: add Docker Hub release workflow + smoke-test CI"
git push origin main
```

### 4c. Watch the first run

1. On GitHub, click the **Actions** tab.
2. You should see two workflow runs: **CI** and **Release**.
3. **CI** runs first (~2-3 min). If it goes red, click into the failed step for the log.
4. **Release** runs in parallel (~3-5 min for first build, much faster after). When green, refresh https://hub.docker.com/r/manasi2210/the-jewel-nest-studio — you'll see new tags: `latest`, `main`, `sha-<short>`.

### 4d. Cutting a versioned release

When you want a stable, version-tagged image:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The **Release** workflow runs again and produces these additional tags on Docker Hub:

- `manasi2210/the-jewel-nest-studio:v0.1.0`
- `manasi2210/the-jewel-nest-studio:0.1.0`
- `manasi2210/the-jewel-nest-studio:0.1`

`latest` only moves on pushes to `main`, so a bad tag doesn't accidentally become "latest".

### 4e. The tagging strategy at a glance

| Trigger | Tags produced |
|---|---|
| Push to `main` | `latest`, `main`, `sha-<short>` |
| Push to feature branch | `<branch-name>`, `sha-<short>` |
| Pull request | `pr-<number>`, `sha-<short>` |
| Tag `v1.2.3` | `v1.2.3`, `1.2.3`, `1.2`, `sha-<short>` |

---

## Part 5 — Deploying the published image

Now anyone (you on a server, a colleague, a CI deploy step) can pull and run the image without the source code:

```bash
docker pull manasi2210/the-jewel-nest-studio:latest

docker run -d --name jewel-app -p 5000:5000 \
  -e DB_HOST=your-mysql-host \
  -e DB_USER=jewel \
  -e DB_PASSWORD=strong-password \
  -e DB_NAME=jewelry_store \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  -v jewel-uploads:/app/uploads \
  -v jewel-sessions:/app/flask_session \
  manasi2210/the-jewel-nest-studio:latest
```

Then point a reverse proxy (nginx, Caddy, Traefik, an ingress controller, …) at `http://host:5000` and you're live.

### Production hardening checklist

Before exposing this to real users:

- [ ] Generate a strong `SECRET_KEY` (`openssl rand -hex 32`) — never reuse the dev value.
- [ ] Use a managed MySQL or a properly backed-up instance, not the compose `db` service.
- [ ] Set `SESSION_COOKIE_SECURE = True` in [config.py](backend/config.py) once you're behind HTTPS.
- [ ] Pin `manasi2210/the-jewel-nest-studio:v0.1.0` (not `:latest`) in production so deploys are deterministic.
- [ ] Mount `/app/uploads` and `/app/flask_session` to persistent volumes (otherwise images and sessions die with the container).
- [ ] Run behind HTTPS — terminate TLS at the proxy.
- [ ] Lock down Docker Hub repo to private if the source contains anything sensitive.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `docker build` says `failed to compute cache key: failed to walk` | You ran `docker build` from `backend/` instead of the repo root | `cd ..` first; the top-level Dockerfile needs both `backend/` and `frontend/` |
| Container starts then exits with `Address already in use` | Something else is already on `:5000` | `docker run -p 5050:5000 …` to remap |
| `/api/health` returns `502` from a reverse proxy | App boot is slower than the proxy's first probe | The Dockerfile sets `start-period=20s`; let the container settle ~20s before probing |
| Login works but UI says "Authentication required" on next page | You're behind a proxy that strips `Set-Cookie`, or you're hitting a different origin | Check the proxy passes cookies through; confirm browser shows the `session` cookie under `:5000` |
| GitHub Actions: `denied: requested access to the resource is denied` | `DOCKERHUB_TOKEN` is wrong, expired, or lacks Write permission | Regenerate the token at hub.docker.com with **Read, Write, Delete** and update the secret |
| GitHub Actions: `unauthorized: incorrect username or password` | `DOCKERHUB_USERNAME` secret has a typo | Edit the secret to be exactly `manasi2210` (no quotes, no spaces) |
| GitHub Actions: `Error response from daemon: pull access denied` for `python:3.11-slim` | Docker Hub rate-limited the runner's anonymous IP | Re-run the workflow; rare and usually transient |
| Multi-arch build is slow | First time only — QEMU emulates `arm64` | Subsequent builds reuse the GHA cache and are much faster |
| Compose says `app` is unhealthy | DB credentials wrong, or DB still starting | `docker compose logs app` and `docker compose logs db`; the `app` service waits on `db` healthcheck so the DB log usually has the answer |

---

## Quick reference

```bash
# Build locally
docker build -t manasi2210/the-jewel-nest-studio:dev .

# Run locally with full stack
docker compose up --build
docker compose exec app python seed.py     # first time only
# → http://localhost:5000

# Push manually
docker login -u manasi2210
docker push manasi2210/the-jewel-nest-studio:latest

# Cut a release (triggers GitHub Actions)
git tag v0.1.0 && git push origin v0.1.0

# Pull and run published image anywhere
docker pull manasi2210/the-jewel-nest-studio:latest
docker run -d -p 5000:5000 --env-file prod.env manasi2210/the-jewel-nest-studio:latest
```

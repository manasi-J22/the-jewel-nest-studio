# Pushing to GitHub — step-by-step

A walkthrough for getting `the-jewel-nest-studio` from your laptop to a private GitHub repository. Follow each step in order. The whole thing takes ~10 minutes the first time.

---

## Step 0 — Before you start

### Confirm git is installed

Open **PowerShell** and run:

```powershell
git --version
```

You should see something like `git version 2.42.0.windows.1`. If not, download Git for Windows from https://git-scm.com/download/win and install with all defaults.

### Configure git (one-time, only if you've never used git on this machine)

```powershell
git config --global user.name "Manasi Jadhav"
git config --global user.email "your-email@example.com"
git config --global init.defaultBranch main
```

Use the same email that's on your GitHub account.

---

## Step 1 — Rename the project folder

Currently the folder is `D:\application`. We'll rename it to `the-jewel-nest-studio`.

> ⚠️ **Stop the API and frontend servers first** if they're still running (Ctrl+C in those PowerShell windows). You can't rename a folder if files inside it are open.

In PowerShell:

```powershell
cd D:\
Rename-Item -Path "application" -NewName "the-jewel-nest-studio"
```

Verify:

```powershell
Test-Path "D:\the-jewel-nest-studio"
```

Should print `True`.

From now on, every command uses the new path:

```powershell
cd D:\the-jewel-nest-studio
```

---

## Step 2 — Initialize the local git repository

```powershell
cd D:\the-jewel-nest-studio
git init
```

Output: `Initialized empty Git repository in D:/the-jewel-nest-studio/.git/`

### Verify the .gitignore is doing its job

The repo already has a `.gitignore` that excludes:

- `.env` (your DB password!)
- `__pycache__/`, `*.pyc`
- `flask_session/`, `logs/`, `uploads/*` (except `.gitkeep`)

Confirm `.env` is NOT going to be committed:

```powershell
git status --ignored | Select-String "\.env"
```

You should see `.env` listed under "Ignored files". **If you see it under "Untracked files" instead, STOP.** Tell me and I'll fix the `.gitignore` before we push.

---

## Step 3 — First commit

Stage everything that isn't ignored:

```powershell
git add .
```

Check what's about to be committed:

```powershell
git status
```

You should see ~50+ files under "Changes to be committed", but **`.env` should NOT be in that list**. If it is, run:

```powershell
git rm --cached backend/.env
echo "Edit .gitignore — .env wasn't excluded"
```

Once `.env` is safely excluded, commit:

```powershell
git commit -m "Initial commit: The Jewel Nest Studio e-commerce app"
```

---

## Step 4 — Create the GitHub repository (web UI)

1. Open https://github.com in your browser. Make sure you're logged in.
2. Click the **`+`** icon in the top-right → **New repository**.
3. Fill in:
   - **Repository name:** `the-jewel-nest-studio`
   - **Description:** "Full-stack jewelry e-commerce — Flask + MySQL + vanilla JS" (optional)
   - **Visibility:** **Private** ⭐
   - **Initialize this repository with:** leave **all three checkboxes UNCHECKED** (no README, no .gitignore, no license — we already have ours).
4. Click **Create repository**.

GitHub now shows you a page titled "Quick setup" with several command snippets. **Stay on that page** — you'll need the repo URL from it.

---

## Step 5 — Create a Personal Access Token (for authentication)

GitHub no longer accepts your password for git pushes — you need a Personal Access Token (PAT).

1. Open https://github.com/settings/tokens?type=beta in your browser.
2. Click **Generate new token** → **Fine-grained token**.
3. Fill in:
   - **Token name:** `the-jewel-nest-studio-push` (or anything memorable)
   - **Expiration:** `90 days` (recommended)
   - **Repository access:** **Only select repositories** → pick `the-jewel-nest-studio`.
   - **Permissions** → expand **Repository permissions**:
     - **Contents:** `Read and write` ⭐
     - Leave all other permissions as `No access` / default.
4. Click **Generate token** at the bottom.
5. **COPY THE TOKEN NOW.** It looks like `github_pat_11ABC123...`. You will not be able to see it again.

> 🔐 **Keep this token private.** It's a password to your repo. Don't paste it into chats, email, screenshots, or commit it.

Paste the token into Notepad temporarily — you'll use it once in the next step.

---

## Step 6 — Connect your local repo to GitHub and push

Back in PowerShell, in `D:\the-jewel-nest-studio`:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/the-jewel-nest-studio.git
```

Replace `YOUR_USERNAME` with your actual GitHub username. (You can copy the exact URL from the GitHub "Quick setup" page — it ends with `.git`.)

Verify:

```powershell
git remote -v
```

You should see `origin  https://github.com/YOUR_USERNAME/the-jewel-nest-studio.git (fetch)` and a `(push)` line.

### Rename the branch to `main` (if it isn't already)

```powershell
git branch -M main
```

### Push

```powershell
git push -u origin main
```

A Windows credential prompt pops up asking for username and password.

- **Username:** your GitHub username
- **Password:** **paste the Personal Access Token** (NOT your GitHub password)

Windows will save the credential, so you won't be prompted again on this machine.

If the push succeeds, you'll see something like:

```
Enumerating objects: 60, done.
...
To https://github.com/YOUR_USERNAME/the-jewel-nest-studio.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

🎉 Your code is now on GitHub. Refresh the GitHub repo page in your browser to see it.

---

## Step 7 — Verify the push (sanity checks)

In your browser, on the GitHub repo page, check:

- [ ] All folders are present: `backend/`, `frontend/`.
- [ ] `README.md` shows the "The Jewel Nest Studio" header with social links.
- [ ] `LICENSE` is recognized — GitHub shows "MIT License" in the right sidebar.
- [ ] `.env` is **NOT visible**. Browse `backend/` and confirm only `.env.example` is there.
- [ ] `uploads/` folder shows only `.gitkeep` (no real images that may have been uploaded during testing).

If `.env` is visible on GitHub:

1. **STOP USING THE CURRENT MYSQL PASSWORD.** Reset it.
2. Tell me — we need to remove it from history (not just the latest commit).

---

## Step 8 — Day-to-day workflow from now on

Whenever you make changes:

```powershell
cd D:\the-jewel-nest-studio
git status                    # see what changed
git add .                     # stage everything
git commit -m "Describe what you changed"
git push                      # send it up to GitHub
```

To pull changes from GitHub (e.g. if you edit something via the web UI, or work from another machine):

```powershell
git pull
```

---

## Update your local app start commands

Your start commands have changed because the folder was renamed. Here they are for reference:

```powershell
# Terminal 1 — API
cd D:\the-jewel-nest-studio\backend
python app.py

# Terminal 2 — Frontend
cd D:\the-jewel-nest-studio\frontend
python -m http.server 8000
```

(Update your `USAGE.md` cheat-sheet too if you saved local notes anywhere — the file already references `the-jewel-nest-studio` so no edit needed.)

---

## Troubleshooting

| Error | What it means | Fix |
|---|---|---|
| `fatal: not a git repository` | You forgot `cd D:\the-jewel-nest-studio` | cd into the right folder |
| `error: failed to push some refs` | Someone (you?) pushed something else to the repo first | `git pull --rebase` then `git push` |
| `remote: Repository not found` | Wrong URL or wrong access | Re-check `git remote -v` and the token's repo permissions |
| `Authentication failed` | Token expired or wrong | Regenerate token, run `git push` — it'll re-prompt |
| `LF will be replaced by CRLF` warnings | Windows line-ending warnings | Harmless. Or run: `git config --global core.autocrlf true` |
| Credential prompt won't accept the token | You typed your GitHub password by mistake | Paste the token — it's the long string starting with `github_pat_` |

---

## Optional polish (after first push)

These are nice-to-have but skip them if you're tired:

- **Add a repo description and tags** on GitHub (Settings → top of the repo page → ⚙️ icon next to "About").
- **Add a screenshot** at the top of `README.md` — take a screenshot of the home page, save it to `docs/preview.png`, and add `![Preview](docs/preview.png)` near the top of the README.
- **Set up branch protection** for `main` (Settings → Branches → Add rule). Required if other people will collaborate.
- **Pin the repo** to your GitHub profile (Profile → Customize your pins).

---

If anything in steps 1-7 doesn't behave the way this guide says, paste me the exact PowerShell output and I'll diagnose it. The single most common stumble is at Step 6 — Windows credential prompt — where people type their GitHub *password* instead of pasting the *token*. If you get "Authentication failed", that's almost certainly it.

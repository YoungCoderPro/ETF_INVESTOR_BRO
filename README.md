# ETF Command Center — Deploy as a permanent website

## What you get
A real URL (e.g. `yourname-etf-center.streamlit.app`) accessible from any device —
phone, laptop, anywhere — that runs permanently, remembers your portfolio, and has
the AI advisor. Free, no server required.

---

## Step 1 — Install Git and create a GitHub account
If you don't have Git: https://git-scm.com/download/win
If you don't have a GitHub account: https://github.com

---

## Step 2 — Create a new private GitHub repository

1. Go to https://github.com/new
2. Name it something like `my-etf-center`
3. Set it to **Private** (your portfolio data stays private)
4. Click "Create repository"

---

## Step 3 — Push your files to GitHub

Open PowerShell in your INVESTY folder and run:

```powershell
git init
git add etf_app.py requirements.txt
git commit -m "Initial ETF Command Center"
git remote add origin https://github.com/YOUR_USERNAME/my-etf-center.git
git push -u origin main
```

Add a `.gitignore` file (create it with Notepad) containing:
```
portfolio.json
.streamlit/secrets.toml
__pycache__/
*.pyc
.etf_price_cache*
```

---

## Step 4 — Deploy on Streamlit Community Cloud (free)

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository → Main file path: `etf_app.py`
5. Click "Deploy" → live in ~2 minutes at `yourname-etf-center.streamlit.app`

---

## Step 5 — Add secrets (API key + persistent database)

### Anthropic API key (AI Advisor tab)
In Streamlit Cloud → your app → Settings → Secrets:
```toml
ANTHROPIC_KEY = "sk-ant-your-key-here"
```
Free key at https://console.anthropic.com (~$5 free credit included)

### Persistent portfolio with Supabase (free cloud database)

Without this, your portfolio.json resets on each deploy. With Supabase it's permanent.

1. Go to https://supabase.com → create free project
2. SQL Editor → run this:
```sql
CREATE TABLE portfolio_trades (
  id TEXT PRIMARY KEY,
  ticker TEXT NOT NULL,
  date_bought DATE NOT NULL,
  amount_usd FLOAT NOT NULL,
  note TEXT DEFAULT '',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE portfolio_trades ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all" ON portfolio_trades FOR ALL USING (true);
```
3. Settings → API → copy your Project URL and anon key
4. Add to Streamlit Secrets:
```toml
ANTHROPIC_KEY = "sk-ant-your-key-here"
SUPABASE_URL  = "https://yourproject.supabase.co"
SUPABASE_KEY  = "your-anon-key"
```
5. Add `supabase>=2.0` to requirements.txt, push to GitHub

---

## Step 6 — Push updates any time

```powershell
git add etf_app.py requirements.txt
git commit -m "Describe your change"
git push
```
Streamlit Cloud auto-redeploys in ~30 seconds.

---

## Phone access right now (no deployment needed)

Look at your terminal for the **Network URL** when the app is running:
```
Network URL: http://10.103.0.123:8501
```
Open that on your phone's browser while on the same WiFi. Instant mobile access.

---

## Cost summary
| Service | Cost |
|---------|------|
| Streamlit Community Cloud | Free |
| GitHub private repo | Free |
| Supabase (500MB DB, 50k req/day) | Free |
| Anthropic API | ~$0.01–0.05 per conversation |

**Total: effectively free for personal use.**
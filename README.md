# ⛳ Golf Swing Tracker & Analytics Dashboard

A personal, mobile-responsive golf analytics web app built with **Streamlit + Supabase** — runs 100% free.

---

## 📁 Project Structure

```
.
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
├── supabase_schema.sql     ← Database DDL (run in Supabase SQL Editor)
├── secrets_template.toml   ← Copy to .streamlit/secrets.toml
└── README.md
```

---

## 🚀 Setup Guide (Step-by-Step)

### 1. Create a Supabase Project (Free)
1. Go to [supabase.com](https://supabase.com) → **New Project**
2. Note your **Project URL** and **anon/public API key** (under Settings → API)

### 2. Create the Database Tables
1. In Supabase, go to **SQL Editor**
2. Paste the contents of `supabase_schema.sql` and run it

### 3. Create the Storage Bucket
1. In Supabase, go to **Storage** → **New Bucket**
2. Name: `swing-clips`
3. Toggle: **Public bucket** ✅
4. Click **Create bucket**

### 4. Set Up Secrets Locally
```bash
mkdir -p .streamlit
cp secrets_template.toml .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your real values
```

Your `.streamlit/secrets.toml` should look like:
```toml
SUPABASE_URL   = "https://xxxx.supabase.co"
SUPABASE_KEY   = "eyJhbGci..."
ADMIN_PASSWORD = "your-secure-password"
STORAGE_BUCKET = "swing-clips"
```

### 5. Install Dependencies & Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

1. Push this repo to **GitHub** (keep `.streamlit/secrets.toml` in `.gitignore`!)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo / branch / `app.py`
4. Under **Advanced settings → Secrets**, paste your secrets (same key-value pairs from `secrets.toml`)
5. Click **Deploy** — done!

---

## 🔐 Authentication Flow

| Mode        | Access                          |
|-------------|---------------------------------|
| Viewer      | Dashboard + Video Gallery       |
| Admin       | + Upload Clips + Log Sessions   |

The sidebar contains a password input. The correct password is stored in Streamlit Secrets (never in code).

---

## 📊 Analytics Features

| Chart | Description |
|-------|-------------|
| **Club Distance** | Average vs Max total distance per club (grouped bar) |
| **Shot Dispersion** | Shot shape frequency filtered by club (grouped bar) |
| **Consistency Score** | Std Dev of distances per club — lower = more consistent |
| **Distance Trend** | Time-series line chart per club (total + carry) |

---

## 🎥 Video Vault

- Filterable by category: Driver, Irons, Woods, Putting
- Inline video playback via Supabase public URLs
- Admin can delete clips from the UI

---

## 📝 Session Logging

- Log individual shots: club, date, total/carry distance
- Visual shot shape selector: Straight / Draw / Fade / Push / Pull / Slice / Hook
- Delete last entry shortcut

---

## 💡 Tips

- **Mobile**: The app is responsive — all layouts use `st.columns` and stack on narrow screens
- **Cache**: Data is cached for 60 seconds; invalidated on every write
- **Free tier limits**: Supabase free tier gives 500 MB DB + 1 GB storage. Streamlit Community Cloud handles apps with no sleeping on activity.

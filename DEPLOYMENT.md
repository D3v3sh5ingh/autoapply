# 🚀 JobPulse Agent - Deployment Guide

## ☁️ Recommended Deployment: Streamlit Community Cloud
This is the easiest, fastest, and **completely free** way to host your JobPulse Agent.

### 📋 Prerequisites
1. **GitHub Account:** Your code must be in a GitHub repository.
2. **Streamlit Account:** Sign up at [share.streamlit.io](https://share.streamlit.io) using your GitHub account.

---

### 🛠️ Step 1: Push Code to GitHub
```bash
git add .
git commit -m "feat: complete multi-tenant saas with oauth"
# Create a new private repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/jobpulse-agent.git
git push -u origin master
```

---

### 🛠️ Step 2: Deploy to Streamlit
1. Go to your [Streamlit Dashboard](https://share.streamlit.io).
2. Click **"New app"**.
3. Select your repository and the `master` branch.
4. Main file path: `src/ui/dashboard.py`.
5. **CRITICAL:** Click **"Advanced settings..."** before deploying!

---

### 🔑 Step 3: Setup Secrets (OAuth)
In the "Secrets" box in Advanced Settings, paste your credentials exactly like this:

```toml
GOOGLE_CLIENT_ID = "your_google_id"
GOOGLE_CLIENT_SECRET = "your_google_secret"
GITHUB_CLIENT_ID = "your_github_id"
GITHUB_CLIENT_SECRET = "your_github_secret"
OAUTH_REDIRECT_URI = "https://your-app-name.streamlit.app"
ENV = "production"
```

---

### 🔗 Step 4: Update Redirect URIs
After deploying, you will get a URL like `https://jobpulse.streamlit.app`. Update your Google/GitHub consoles:
- **Google Authorized Redirect URI:** `https://your-app-name.streamlit.app`
- **GitHub Callback URL:** `https://your-app-name.streamlit.app`

---

## 🏗️ Alternative: Docker on VPS
If you need persistent database storage (Streamlit Cloud storage is temporary), use Docker on a Linux server:
1. Clone your repo to the server.
2. Run `docker-compose up -d --build`.
3. Your data will persist in the `/data` folder on the server.

---
**JobPulse Agent** | Production Multi-Tenant Architecture

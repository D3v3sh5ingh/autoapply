# 🚀 JobPulse Agent - Deployment Guide

## Quick Deployment Options

### Option 1: Streamlit Community Cloud (FREE, EASIEST)
Perfect for sharing with friends or small teams.

**Steps:**
1. Push your code to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/jobpulse-agent.git
   git push -u origin master
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repo: `jobpulse-agent`
6. Main file: `src/ui/dashboard.py`
7. Click "Deploy"

**Done!** You'll get a URL like `https://yourapp.streamlit.app`

### Option 2: Docker on Your Server (FULL CONTROL)
For running on your own VPS (DigitalOcean, AWS, etc.)

**Steps:**
1. **Get a server** (e.g., DigitalOcean $6/month droplet)
   
2. **SSH into server and install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo apt-get install docker-compose
   ```

3. **Clone your repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/jobpulse-agent.git
   cd jobpulse-agent
   ```

4. **Deploy:**
   ```bash
   docker-compose up -d --build
   ```

5. **Access at:** `http://your-server-ip:8501`

**Optional - Add domain:**
```bash
# Install nginx
sudo apt install nginx

# Point domain to server, configure nginx proxy
# (Google: "nginx reverse proxy streamlit")
```

### Option 3: Render (FREE with limitations)
Good middle ground - free tier available.

**Steps:**
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create "New Web Service"
4. Connect GitHub repo
5. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run src/ui/dashboard.py --server.port=$PORT --server.address=0.0.0.0`
6. Deploy

**Free tier:** App sleeps after 15 min inactivity

## What About OAuth?

**For Personal/Private Use:**
- You don't need real OAuth
- Demo mode works perfectly
- Keep using as-is

**For Public Deployment (100+ users):**
1. Get OAuth credentials:
   - [Google Console](https://console.cloud.google.com/apis/credentials)
   - [GitHub OAuth](https://github.com/settings/developers)

2. Add to server environment:
   ```bash
   # On your server:
   cp .env.example .env
   nano .env  # Add your credentials
   ```

3. Restart app

## Database Persistence

**Streamlit Cloud / Render:**
- Data stored in container (lost on restart)
- For persistence, use external DB (PostgreSQL on Render/Supabase)

**Docker on VPS:**
- Data persists in `autoapply.db` file
- Automatic backup recommended:
  ```bash
  # Add to crontab
  0 2 * * * cp /path/to/autoapply.db /backups/autoapply-$(date +\%Y\%m\%d).db
  ```

## Security Checklist

Before going live:
- [ ] Change default admin credentials (if using real OAuth)
- [ ] Set rate limits appropriate for your audience
- [ ] Add HTTPS (use Cloudflare or Let's Encrypt)
- [ ] Review what data you're storing
- [ ] Add monitoring (UptimeRobot for free uptime checks)

## Cost Estimate

| Option | Cost | Best For |
|--------|------|----------|
| Streamlit Cloud | FREE | Personal use, demos |
| Render Free | FREE | Testing, low traffic |
| DigitalOcean VPS | $6/mo | Full control, stable |
| AWS/GCP | $10-50/mo | Enterprise scale |

## Recommended Path

**For You (Right Now):**
1. Use Streamlit Cloud (free, 5 minutes to deploy)
2. Get feedback from users
3. If traffic grows, migrate to VPS

## Quick Deploy Script

```bash
#!/bin/bash
# deploy.sh - Run this to deploy updates

git add -A
git commit -m "deploy: $(date)"
git push origin master

# If using Docker on VPS:
ssh your-server "cd jobpulse-agent && git pull && docker-compose up -d --build"
```

---
**Ready to deploy?** Pick Option 1 (Streamlit Cloud) for fastest results!

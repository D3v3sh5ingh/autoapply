# Quick Deploy to Fly.io (FREE)

## 1. Install Fly CLI
```bash
# Windows (PowerShell)
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Or download from: https://fly.io/docs/hands-on/install-flyctl/
```

## 2. Sign Up (Free Tier)
```bash
fly auth signup
# or if you have account:
fly auth login
```

## 3. Deploy (One Command)
```bash
# From your project folder
fly launch

# When prompted:
# - App name: jobpulse-agent (or your choice)
# - Region: Choose closest to you
# - PostgreSQL? NO
# - Redis? NO
```

## 4. Create Persistent Volume
```bash
fly volumes create jobpulse_data --size 1
```

## 5. Deploy!
```bash
fly deploy
```

## 6. Done! 🎉
Your app will be live at: `https://jobpulse-agent.fly.dev`

## Free Tier Limits
- ✅ 3 apps
- ✅ 1GB persistent storage
- ✅ 160GB bandwidth/month
- ⚠️ App sleeps after inactivity (cold start ~2s)

## To Update App Later
```bash
git add -A
git commit -m "update"
fly deploy
```

## View Logs
```bash
fly logs
```

## Check Status
```bash
fly status
```

---

**Cost:** $0/month on free tier! Perfect for MVP testing.

# 🚀 OAuth Setup Guide for Production Deployment

## Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing 
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Application type**: Web application
6. Add **Authorized redirect URIs**:
   - For development: `http://localhost:8501`
   - For production: `https://your-app.fly.dev`
7. Copy **Client ID** and **Client Secret**

## Step 2: Create GitHub OAuth App

1. Go to [GitHub Settings → Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in:
   - **Application name**: JobPulse Agent
   - **Homepage URL**: `https://your-app.fly.dev` (or `http://localhost:8501` for dev)
   - **Authorization callback URL**: Same as homepage URL
4. Click **Register application**
5. Click **Generate a new client secret**
6. Copy **Client ID** and **Client Secret**

## Step 3: Configure .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials:
GOOGLE_CLIENT_ID=your-actual-client-id
GOOGLE_CLIENT_SECRET=your-actual-secret

GITHUB_CLIENT_ID=your-actual-client-id  
GITHUB_CLIENT_SECRET=your-actual-secret

# For local testing:
OAUTH_REDIRECT_URI=http://localhost:8501
ENV=dev

# For production (update after deploying to Fly.io):
# OAUTH_REDIRECT_URI=https://your-app.fly.dev
# ENV=production
```

## Step 4: Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run src/ui/dashboard.py

# Try logging in with Google/GitHub
```

## Step 5: Deploy to Fly.io

```bash
# Set production environment variables
fly secrets set GOOGLE_CLIENT_ID="your-client-id"
fly secrets set GOOGLE_CLIENT_SECRET="your-secret"
fly secrets set GITHUB_CLIENT_ID="your-client-id"
fly secrets set GITHUB_CLIENT_SECRET="your-secret"
fly secrets set OAUTH_REDIRECT_URI="https://your-app.fly.dev"
fly secrets set ENV="production"

# Deploy
fly deploy
```

## Step 6: Update OAuth App Redirect URIs

After deploying, go back to Google and GitHub OAuth settings and add your production URL:
- Google Cloud Console → Add `https://your-app.fly.dev` to authorized redirect URIs
- GitHub OAuth App → Update Authorization callback URL to `https://your-app.fly.dev`

## Troubleshooting

**"OAuth not configured" error:**
- Check `.env` file exists and has correct values
- Make sure no spaces around `=` in .env file
- Restart Streamlit after changing .env

**"Redirect URI mismatch" error:**
- Ensure OAUTH_REDIRECT_URI matches exactly what's in OAuth app settings
- Check for trailing slashes - use same format everywhere
- For Fly.io: use `https://` not `http://`

**"Invalid client" error:**
- Double-check Client ID and Secret are copied correctly
- No extra spaces or quotes in credentials

---

**Security Notes:**
- Never commit `.env` file to git (it's in .gitignore)
- Use Fly.io secrets for production (not .env file)
- Rotate secrets if they're ever exposed

#!/bin/bash
# Fly.io deployment script

echo "🚀 Deploying JobPulse Agent to Fly.io..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl not found. Installing..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/home/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
fi

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Please log in to Fly.io:"
    flyctl auth login
fi

# Check if app exists
if ! flyctl apps list | grep -q "jobpulse-agent"; then
    echo "📦 Creating new Fly.io app..."
    flyctl apps create jobpulse-agent
    
    echo "💾 Creating persistent volume..."
    flyctl volumes create jobpulse_data --region iad --size 1
fi

# Set secrets (OAuth credentials)
echo "🔑 Setting OAuth secrets..."
echo "Enter your Google Client ID:"
read GOOGLE_CLIENT_ID
flyctl secrets set GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID"

echo "Enter your Google Client Secret:"
read -s GOOGLE_CLIENT_SECRET
flyctl secrets set GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET"

echo "Enter your GitHub Client ID:"
read GITHUB_CLIENT_ID
flyctl secrets set GITHUB_CLIENT_ID="$GITHUB_CLIENT_ID"

echo "Enter your GitHub Client Secret:"
read -s GITHUB_CLIENT_SECRET
flyctl secrets set GITHUB_CLIENT_SECRET="$GITHUB_CLIENT_SECRET"

# Deploy
echo "🚢 Deploying application..."
flyctl deploy

echo "✅ Deployment complete!"
echo "🌐 Your app is live at: https://jobpulse-agent.fly.dev"
echo ""
echo "📊 Monitor status: flyctl status"
echo "📝 View logs: flyctl logs"

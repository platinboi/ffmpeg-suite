# Railway Deployment Guide

Quick guide to deploy the FFmpeg Text Overlay API to Railway.

## Prerequisites

- Railway account (sign up at https://railway.app)
- GitHub repository with your code (or deploy from local)
- Your API key from first startup (or check `data/api_keys.json`)

## Step 1: Install Railway CLI (Optional)

```bash
npm i -g @railway/cli
railway login
```

Or deploy via Railway web dashboard (easier for first time).

## Step 2: Create New Project

### Option A: Deploy from GitHub (Recommended)

1. Push your code to GitHub
2. Go to https://railway.app/new
3. Click **Deploy from GitHub repo**
4. Select your repository
5. Railway will auto-detect Python and start building

### Option B: Deploy from CLI

```bash
cd /Users/luca/Desktop/Projects/ffmpeg-scripts
railway init
railway up
```

## Step 3: Configure Environment Variables

In Railway dashboard, go to your project → **Variables** tab and add:

### Required Variables

```bash
# Port (Railway automatically provides this, but you can override)
PORT=8000

# Optional: R2 Storage (can enable later)
R2_ENABLED=false

# If you enable R2 later, add these:
# R2_ACCOUNT_ID=your_account_id
# R2_ACCESS_KEY_ID=your_access_key
# R2_SECRET_ACCESS_KEY=your_secret_key
# R2_BUCKET_NAME=ffmpeg-text-overlay-prod
```

### Railway Auto-Provides

Railway automatically provides:
- `PORT` - The port your app should listen on
- `RAILWAY_ENVIRONMENT` - Development/production
- Public URL

## Step 4: Configure Build Settings

Railway should auto-detect, but verify:

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
python main.py
```

### Runtime
- **Language**: Python 3.11+
- **Buildpack**: Auto-detected

## Step 5: Install FFmpeg

Railway doesn't include FFmpeg by default. Create a `Nixpacks.toml` file:

```toml
# Nixpacks.toml
[phases.setup]
nixPkgs = ['ffmpeg']

[phases.install]
cmds = ['pip install -r requirements.txt']

[start]
cmd = 'python main.py'
```

Or use a `Dockerfile` (more control):

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

If using Dockerfile, create `.dockerignore`:
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.git
.gitignore
*.md
data/
temp/
ui/
node_modules/
```

## Step 6: Deploy

Railway will automatically deploy when you push to GitHub or run:

```bash
railway up
```

Watch the deployment logs in the Railway dashboard.

## Step 7: Get Your API URL

Once deployed, Railway provides a public URL like:
```
https://your-app-name.up.railway.app
```

You can also add a custom domain in Railway settings.

## Step 8: Get Your API Key

On **first deployment**, check Railway logs for the bootstrap message:

```
============================================================
🎉 FIRST TIME SETUP COMPLETE!
============================================================
✓ User ID: default
✓ API Key: sk_live_xxxxx...
============================================================
⚠️  SAVE THIS API KEY - IT WON'T BE SHOWN AGAIN!
============================================================
```

**IMPORTANT**: Save this API key immediately! It's only shown once.

If you miss it, you can:
1. Check local `data/api_keys.json` before deploying
2. Or SSH into Railway container and read the file

## Step 9: Test Your Deployment

Test without API key (should fail):
```bash
curl https://your-app-name.up.railway.app/templates
```

Response:
```json
{
  "status": "error",
  "message": "Missing API key. Provide X-API-Key header or Authorization: Bearer <key>"
}
```

Test with API key (should work):
```bash
curl https://your-app-name.up.railway.app/templates \
  -H "X-API-Key: sk_live_xxxxx..."
```

Response:
```json
{
  "templates": {...},
  "count": 1
}
```

## Step 10: Use in n8n

In your n8n HTTP Request node:

**URL**: `https://your-app-name.up.railway.app/overlay/url`

**Method**: POST

**Authentication**: None (we use custom header)

**Headers**:
```json
{
  "X-API-Key": "sk_live_xxxxx...",
  "Content-Type": "application/json"
}
```

**Body** (JSON):
```json
{
  "url": "{{ $json.image_url }}",
  "text": "{{ $json.text }}",
  "template": "default"
}
```

**Response**: Binary file (processed image/video)

## Persistent Storage Note

Railway provides ephemeral storage by default. The `data/` directory with your API keys and usage records will persist between deploys, but:

- If Railway restarts your container, `data/` persists
- If you redeploy, `data/` might reset (depends on Railway's behavior)

**Recommended**: After first deploy, **download `data/api_keys.json`** and keep it safe. If the container resets, you can re-upload it or add it to your repo (but add to `.gitignore` for security).

Or use Railway Volumes:
1. Go to project settings
2. Add Volume
3. Mount path: `/app/data`
4. This ensures `data/` always persists

## Monitoring

### View Logs
```bash
railway logs
```

Or in Railway dashboard → **Deployments** → Click deployment → **View Logs**

### Check Usage
SSH into container:
```bash
railway shell
cat data/usage_records.json
```

Or add an API endpoint to view usage (future enhancement).

## Costs

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month for 500 hours
- **Pro Plan**: $20/month + usage-based compute
- **Free Trial**: $5 credit (enough for testing)

FFmpeg processing is CPU-intensive, so monitor usage.

## Troubleshooting

### FFmpeg not found
- Ensure `Nixpacks.toml` includes `ffmpeg` in `nixPkgs`
- Or use Dockerfile with `apt-get install ffmpeg`

### Fonts not loading
- Ensure `fonts/` directory is copied in Dockerfile
- Check file paths are correct

### API key not working
- Check Railway logs for bootstrap message
- Verify header name is `X-API-Key` (case-sensitive)
- Ensure no extra spaces in API key

### Port binding error
- Don't hardcode port 8000, use `os.getenv("PORT", 8000)`
- Railway dynamically assigns ports

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Save API key
3. ✅ Test with n8n workflow
4. Optional: Set up R2 storage for outputs
5. Optional: Add usage monitoring endpoint
6. Optional: Add custom domain

## Environment Variables Summary

```bash
# Railway Auto-Provides
PORT=8000                          # Auto-assigned by Railway

# Optional R2 Storage (can enable later)
R2_ENABLED=false
# R2_ACCOUNT_ID=xxx
# R2_ACCESS_KEY_ID=xxx
# R2_SECRET_ACCESS_KEY=xxx
# R2_BUCKET_NAME=ffmpeg-text-overlay-prod
```

## Support

If you encounter issues:
1. Check Railway deployment logs
2. Test locally first: `python main.py`
3. Verify FFmpeg is installed: `ffmpeg -version`
4. Check MULTI_TENANT_SETUP.md for architecture details

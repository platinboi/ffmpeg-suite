# Quick Start Deployment Guide

## Prerequisites
- Python 3.11+
- FFmpeg installed
- PostgreSQL (Neon) database
- API Key: `sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U`

---

## Option 1: ngrok (Immediate Testing - 5 minutes)

### 1. Install ngrok
```bash
brew install ngrok
# OR download from: https://ngrok.com/download
```

### 2. Start Backend (if not already running)
```bash
cd /Users/luca/Desktop/Projects/ffmpeg-scripts
python main.py
# Server runs on http://localhost:8000
```

### 3. Expose with ngrok
```bash
ngrok http 8000
```

### 4. Copy ngrok URL
You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

### 5. Test with curl
```bash
curl https://abc123.ngrok.io/health
```

### 6. Use in n8n
- API URL: `https://abc123.ngrok.io`
- Add header: `X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U`
- Test endpoint: POST `/overlay/merge`

**Limitations:**
- URL changes on restart
- Requires your machine running 24/7
- Free tier has connection limits

---

## Option 2: Railway (Production - 30 minutes)

### Pre-Deployment Checklist
✅ DATABASE_URL security fixed (no hardcoded credentials)
✅ CORS configurable via environment variable
✅ .env file created for local development
✅ python-dotenv loaded in main.py
✅ Dockerfile ready
✅ railway.toml configured

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Get $5 free credit

### 2. Connect GitHub Repository
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your repos
4. Select: `ffmpeg-scripts` repository
5. Click "Deploy Now"

### 3. Configure Environment Variables
In Railway project settings → Variables, add:

**Required:**
```
DATABASE_URL=postgresql://neondb_owner:npg_Y3uQc9xVXgze@ep-bitter-frog-ahv64lf5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Optional (for production):**
```
CORS_ORIGINS=https://your-frontend.com,https://n8n.yoursite.com
```

### 4. Configure Railway Volume (for API keys)
1. In Railway project → Settings → Volumes
2. Click "Add Volume"
3. Mount path: `/app/data`
4. Click "Add"

### 5. Upload API Keys to Volume
Option A: Use Railway CLI
```bash
railway login
railway link
railway volumes upload data ./data/api_keys.json
```

Option B: Manually via Railway dashboard
1. Open Volume in Railway UI
2. Upload `data/api_keys.json` file

### 6. Deploy and Get URL
1. Railway auto-deploys on push
2. Get your URL: `https://your-app.up.railway.app`
3. Custom domain available in settings

### 7. Test Deployment
```bash
# Health check
curl https://your-app.up.railway.app/health

# List templates
curl https://your-app.up.railway.app/templates

# Test merge endpoint
curl -X POST https://your-app.up.railway.app/overlay/merge \
  -H "X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U" \
  -H "Content-Type: application/json" \
  -d '{
    "clips": [
      {
        "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
        "text": "Test Clip 1",
        "template": "default"
      },
      {
        "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
        "text": "Test Clip 2",
        "template": "default"
      }
    ],
    "output_format": "mp4"
  }' \
  --output test_merge.mp4
```

### 8. Monitor Deployment
- Logs: Railway dashboard → Deployments → View logs
- Metrics: Railway dashboard → Metrics
- Health: `https://your-app.up.railway.app/health`

---

## API Endpoints Reference

### Merge Two Clips
```bash
POST /overlay/merge
Headers:
  X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U
  Content-Type: application/json

Body:
{
  "clips": [
    {
      "url": "https://video-url-1.mp4",
      "text": "First clip text",
      "template": "default"
    },
    {
      "url": "https://video-url-2.mp4",
      "text": "Second clip text",
      "template": "default"
    }
  ],
  "output_format": "mp4"
}
```

### Single Clip Overlay
```bash
POST /overlay/url
Headers:
  X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U
  Content-Type: application/json

Body:
{
  "url": "https://video-url.mp4",
  "text": "My text overlay",
  "template": "default",
  "output_format": "mp4"
}
```

### List Templates
```bash
GET /templates
# No authentication required
```

### Health Check
```bash
GET /health
# No authentication required
```

---

## n8n Integration

### HTTP Request Node Configuration

**Method:** POST
**URL:** `https://your-app.railway.app/overlay/merge`

**Headers:**
```
X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "clips": [
    {
      "url": "{{ $json.video_url_1 }}",
      "text": "{{ $json.text_1 }}",
      "template": "default"
    },
    {
      "url": "{{ $json.video_url_2 }}",
      "text": "{{ $json.text_2 }}",
      "template": "default"
    }
  ],
  "output_format": "mp4"
}
```

**Response Options:**
- Binary Property: `data`
- Output: Download file

---

## Troubleshooting

### "DATABASE_URL environment variable is required"
**Solution:** Set DATABASE_URL in Railway environment variables or `.env` file locally

### "FFmpeg not found"
**Railway:** Already installed via Dockerfile
**Local:** Install FFmpeg: `brew install ffmpeg`

### "Font not found"
**Railway:** Fonts auto-downloaded in Dockerfile
**Local:** Fonts should be in `./fonts/` directory

### ngrok URL changes on restart
**Solution:**
- Free tier: Accept the changing URL
- Paid tier ($8/month): Get static domain
- Production: Use Railway instead

### CORS errors
**Solution:** Set `CORS_ORIGINS` environment variable to allowed domains (comma-separated)

---

## Cost Breakdown

### ngrok
- **Free:** Basic tunneling, changing URLs
- **Pro ($8/mo):** Static domains, custom URLs

### Railway
- **Hobby ($5/mo):** 500 hours/month, $5 credit included
- **Pro ($20/mo):** Unlimited hours
- **Enterprise:** Custom pricing

### Recommended for Production
- Railway Hobby: $5/month
- Neon PostgreSQL: Free tier (sufficient)
- Total: **$5/month**

---

## Next Steps

1. **Now:** Test with ngrok (5 minutes)
2. **This week:** Deploy to Railway (30 minutes)
3. **Production:**
   - Set up custom domain
   - Configure CORS for specific origins
   - Set up monitoring/alerts
   - Consider scaling resources if needed

---

## Support & Documentation

- **API Documentation:** `https://your-app.railway.app/docs`
- **curl Examples:** See `CURL_EXAMPLES.md`
- **Full Railway Guide:** See `RAILWAY_DEPLOYMENT.md`
- **API Key Management:** Use `python generate_api_key.py`

---

## Security Notes

✅ **Fixed:** DATABASE_URL moved to environment variables
✅ **Fixed:** CORS configurable via CORS_ORIGINS
✅ **Implemented:** API key authentication on all overlay endpoints
✅ **Implemented:** Multi-tenant usage tracking
✅ **Implemented:** Connection pooling (2-10 connections)

⚠️ **TODO for Production:**
- Rotate API keys regularly
- Set specific CORS origins (not `*`)
- Monitor usage per user
- Set up Railway Volume backups

---

**Project Status:** ✅ Production-Ready
**Last Updated:** 2025-11-18

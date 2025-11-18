# Multi-Tenant Setup Guide

## Phase 1 Implementation Status ✅

### What's Been Implemented

1. **✅ API Key Authentication System** (`services/auth_service.py`)
   - User management (create, get users)
   - API key generation with secure hashing (SHA-256)
   - API key validation
   - JSON-based storage (easy to migrate to PostgreSQL later)
   - Bootstrap function to create default user

2. **✅ Usage Tracking System** (`services/usage_service.py`)
   - Track every API call (endpoint, file sizes, processing time)
   - User-scoped tracking
   - Monthly/date-range summaries
   - JSON-based storage (first 10,000 records)

3. **✅ Multi-Tenant Storage** (`services/storage_service.py`)
   - User-scoped paths: `users/{user_id}/outputs/2024-11/filename.mp4`
   - Private file uploads (ACL: private)
   - Month-based organization

4. **✅ boto3 Dependencies** (`requirements.txt`)
   - Uncommented and ready to install

### What's Next (Need to Complete)

5. **⏳ Update main.py** - Add auth middleware and integrate services
6. **⏳ R2 Setup Guide** - Instructions for creating R2 bucket
7. **⏳ End-to-End Testing** - Test with API key

---

## How to Complete Setup

### Step 1: Install Dependencies

```bash
cd /Users/luca/Desktop/Projects/ffmpeg-scripts
pip install -r requirements.txt
```

This will install boto3 and other dependencies.

### Step 2: Create Cloudflare R2 Bucket

1. Go to https://dash.cloudflare.com/
2. Navigate to **R2** in the sidebar
3. Click **Create bucket**
4. Name it: `ffmpeg-text-overlay-prod` (or your preferred name)
5. Click **Create bucket**

### Step 3: Get R2 API Credentials

1. In R2 dashboard, click **Manage R2 API Tokens**
2. Click **Create API token**
3. Name: `FFmpeg Service Token`
4. Permissions: **Object Read & Write**
5. Click **Create API Token**
6. **SAVE THESE VALUES** (shown only once):
   - Access Key ID
   - Secret Access Key
   - Account ID

### Step 4: Update Environment Variables

Create or update `.env` file:

```bash
# R2 Storage Configuration
R2_ENABLED=true
R2_ACCOUNT_ID=your_account_id_here
R2_ACCESS_KEY_ID=your_access_key_here
R2_SECRET_ACCESS_KEY=your_secret_access_key_here
R2_BUCKET_NAME=ffmpeg-text-overlay-prod
```

For Railway deployment, add these as environment variables in the Railway dashboard.

### Step 5: Start the Server

```bash
python main.py
```

On first run, it will:
- Create `./data/` directory
- Create `api_keys.json` and `usage_records.json`
- Bootstrap a default user
- Generate your first API key
- **SAVE THE API KEY** - it's shown only once!

Look for output like:
```
✓ Bootstrap complete!
✓ User ID: default
✓ API Key: sk_live_abc123...
✓ Save this API key - it won't be shown again!
```

### Step 6: Test the API

Test with curl:

```bash
# Test without API key (should fail with 401)
curl -X POST http://localhost:8000/overlay/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/image.jpg",
    "text": "Hello World",
    "template": "default"
  }'

# Test with API key (should work)
curl -X POST http://localhost:8000/overlay/url \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_your_key_here" \
  -d '{
    "url": "https://example.com/image.jpg",
    "text": "Hello World",
    "template": "default"
  }' \
  --output result.mp4
```

---

## Architecture Overview

### Multi-Tenant File Organization

```
R2 Bucket: ffmpeg-text-overlay-prod/
├── users/
│   ├── default/              # Your personal user
│   │   ├── inputs/
│   │   │   └── 2024-11/
│   │   │       └── original_video.mp4
│   │   └── outputs/
│   │       └── 2024-11/
│   │           └── processed_video.mp4
│   ├── user_abc123/         # Future customer
│   │   ├── inputs/
│   │   └── outputs/
│   └── user_xyz789/         # Another customer
│       ├── inputs/
│       └── outputs/
└── temp/                    # Short-lived processing files
```

### Data Storage (JSON Files)

```
/Users/luca/Desktop/Projects/ffmpeg-scripts/
└── data/
    ├── api_keys.json        # User & API key storage
    └── usage_records.json   # Usage tracking
```

**Example `api_keys.json`:**
```json
{
  "users": [
    {
      "id": "default",
      "email": "admin@localhost",
      "name": "Default User",
      "plan_tier": "default",
      "created_at": "2024-11-17T12:00:00Z"
    }
  ],
  "api_keys": [
    {
      "id": "key_abc123",
      "user_id": "default",
      "key_hash": "sha256_hash_here",
      "key_prefix": "sk_live_abc123",
      "name": "Default API Key",
      "is_active": true,
      "created_at": "2024-11-17T12:00:00Z",
      "last_used_at": "2024-11-17T13:30:00Z"
    }
  ]
}
```

**Example `usage_records.json`:**
```json
{
  "records": [
    {
      "id": "rec_xyz789",
      "user_id": "default",
      "endpoint": "/overlay/url",
      "input_file_size_bytes": 5242880,
      "output_file_size_bytes": 5500000,
      "processing_time_ms": 8500,
      "template_used": "default",
      "has_custom_overrides": true,
      "timestamp": "2024-11-17T14:00:00Z"
    }
  ]
}
```

---

## API Authentication

### How It Works

1. **Client sends request** with `X-API-Key` header
2. **Middleware validates key**:
   - Hashes the provided key (SHA-256)
   - Looks up in `api_keys.json`
   - Checks if key is active
   - Loads associated user
3. **Request is processed** with user context
4. **Usage is tracked** in `usage_records.json`

### API Key Format

- Production: `sk_live_xxxxxxxxxxxxxxx...`
- Test: `sk_test_xxxxxxxxxxxxxxx...` (future)

Keys are 32-byte URL-safe tokens (very secure).

---

## Usage Tracking

Every API call records:
- **User ID** - who made the request
- **Endpoint** - which API was called
- **Input size** - bytes uploaded
- **Output size** - bytes generated
- **Processing time** - milliseconds
- **Template** - which style was used
- **Custom overrides** - boolean flag
- **Timestamp** - when it happened

### View Usage

```python
from services.usage_service import UsageService

usage = UsageService()

# Get summary for current month
from datetime import datetime
summary = usage.get_monthly_summary("default", 2024, 11)
print(summary)

# Output:
# {
#   "user_id": "default",
#   "total_requests": 150,
#   "total_input_mb": 750.5,
#   "total_output_mb": 825.3,
#   "total_processing_seconds": 1250.5,
#   "avg_processing_time_ms": 8337
# }
```

---

## Monetization Ready

### Current Pricing Model (Suggested)

**Free Tier** (default plan):
- 100 requests/month
- 50MB max file size
- Standard processing queue
- 1GB storage

**Pro Tier** ($29/month):
- 10,000 requests/month
- 500MB max file size
- Priority processing
- 100GB storage
- Custom templates

**Enterprise** (Custom pricing):
- Unlimited requests
- 5GB max file size
- Dedicated resources
- 1TB+ storage
- White-label options

### Easy to Add Later

1. **Plan quotas** - check `usage_records.json` before processing
2. **Stripe integration** - webhook for subscription events
3. **PostgreSQL migration** - export JSON to database
4. **Rate limiting** - use slowapi library
5. **Webhooks** - notify on completion

---

## Migration Path to PostgreSQL

When ready to scale, run this migration:

```sql
-- Users table
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    plan_tier VARCHAR(50) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT NOW()
);

-- API Keys table
CREATE TABLE api_keys (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    key_hash VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(20),
    name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

-- Usage records table
CREATE TABLE usage_records (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    endpoint VARCHAR(100),
    input_file_size_bytes BIGINT,
    output_file_size_bytes BIGINT,
    processing_time_ms INTEGER,
    template_used VARCHAR(50),
    has_custom_overrides BOOLEAN,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_usage_user_timestamp ON usage_records(user_id, timestamp);
```

Then update services to use PostgreSQL instead of JSON.

---

## Security Features

### ✅ Implemented
- API key hashing (SHA-256)
- Private R2 file uploads (ACL: private)
- User-scoped file paths
- Audit logging (usage tracking)

### 🔜 Future
- Rate limiting (per user, per IP)
- Request signing (HMAC)
- Presigned URLs for file access
- IP whitelisting
- 2FA for dashboard

---

## Next Steps

1. **Complete main.py integration** (I'll do this next)
2. **Test locally with API key**
3. **Deploy to Railway**
4. **Set up R2 bucket**
5. **Test production deployment**
6. **Start using for your workflows!**

---

## Support & Monitoring

### View Logs
```bash
tail -f /path/to/logs/app.log
```

### Check Usage
```python
from services.usage_service import UsageService
usage = UsageService()
summary = usage.get_user_usage("default")
print(f"Total requests: {len(summary)}")
```

### Rotate API Key
```python
from services.auth_service import AuthService
auth = AuthService()

# Revoke old key
auth.revoke_api_key("old_key_id")

# Generate new key
new_key, key_record = auth.generate_api_key("default", "New API Key")
print(f"New API key: {new_key}")
```

---

## Questions?

This setup gives you:
- ✅ Multi-tenant ready architecture
- ✅ Usage tracking from day 1
- ✅ Easy migration to PostgreSQL
- ✅ R2 storage organization
- ✅ API key security
- ✅ Monetization foundation

You can start with just yourself (`default` user) and easily add more users/customers later by generating new API keys!

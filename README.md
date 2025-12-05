# FFmpeg Text Overlay API

A production-ready FastAPI service for adding customizable text overlays to images and videos using FFmpeg. Designed for Railway deployment with Cloudflare R2 integration.

## Features

- **URL-First Design**: Process files directly from Cloudflare R2 or any public URL
- **File Upload Support**: Backup option for direct file uploads
- **Style Templates**: Predefined text styles (default, bold, minimal, cinematic)
- **Full Customization**: Override any style parameter (font, size, colors, position, effects)
- **Inter Font**: Professional typography with Regular and Bold weights
- **Auto Cleanup**: Automatic temporary file management
- **Railway Ready**: One-click deployment with Docker
- **R2 Integration**: Optional Cloudflare R2 upload support

## Quick Start

### Local Development

1. **Install FFmpeg**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Check installation
ffmpeg -version
```

2. **Clone and Setup**:
```bash
cd ffmpeg-scripts
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Download Inter Font** (if not using Docker):
   - Download from: https://github.com/rsms/inter/releases
   - Extract and place `Inter-Regular.ttf` and `Inter-Bold.ttf` in `fonts/` directory

4. **Run Locally**:
```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

5. **Test the API**:
```bash
# Visit the interactive docs
open http://localhost:8000/docs
```

## API Endpoints

### 1. Process from URL (Primary)

**Endpoint**: `POST /overlay/url`

Process files hosted on Cloudflare R2 or any public URL.

```bash
curl -X POST "http://localhost:8000/overlay/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-bucket.r2.dev/video.mp4",
    "text": "Hello World",
    "template": "default"
  }' \
  --output result.mp4
```

**Request Body**:
```json
{
  "url": "https://your-bucket.r2.dev/video.mp4",
  "text": "Your Text Here",
  "template": "bold",
  "output_format": "same",
  "overrides": {
    "font_size": 64,
    "text_color": "#FFFFFF",
    "border_width": 3,
    "position": "bottom-center"
  }
}
```

### 2. Process from Upload (Backup)

**Endpoint**: `POST /overlay/upload`

Upload files directly when they're not hosted on a CDN.

```bash
curl -X POST "http://localhost:8000/overlay/upload" \
  -F "file=@video.mp4" \
  -F "text=Hello World" \
  -F "template=cinematic" \
  --output result.mp4
```

**With Overrides**:
```bash
curl -X POST "http://localhost:8000/overlay/upload" \
  -F "file=@image.jpg" \
  -F "text=Custom Text" \
  -F "template=default" \
  -F 'overrides={"font_size": 72, "text_color": "yellow", "position": "top-center"}' \
  --output result.jpg
```

### 3. List Templates

**Endpoint**: `GET /templates`

```bash
curl http://localhost:8000/templates
```

**Response**:
```json
{
  "templates": {
    "default": {
      "font_size": 48,
      "text_color": "white",
      "border_width": 2,
      "position": "center",
      ...
    },
    "bold": { ... },
    "minimal": { ... },
    "cinematic": { ... }
  },
  "count": 4
}
```

### 5. Outfit Collage (New)

**Endpoint**: `POST /outfit`

Generate a 5–7 second 9:16 video using 9 square product images laid out exactly like `OUTFIT-EXAMPLE.jpg`, with configurable title and subtitle. Default duration is 5s with 1.5s fade-in from black. Text style uses white with black outline/shadow (same as example).

```bash
curl -X POST "http://localhost:8000/outfit" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-key>" \
  -d '{
    "image_urls": [
      "https://example.com/img1.jpg",
      "https://example.com/img2.jpg",
      "https://example.com/img3.jpg",
      "https://example.com/img4.jpg",
      "https://example.com/img5.jpg",
      "https://example.com/img6.jpg",
      "https://example.com/img7.jpg",
      "https://example.com/img8.jpg",
      "https://example.com/img9.jpg"
    ],
    "main_title": "Choose your school outfit:",
    "subtitle": "(shop in bio)",
    "duration": 5,
    "fade_in": 1.5,
    "response_format": "url"
  }'
```

**Key parameters**
- `image_urls` (required): exactly 9 image URLs (JPG/PNG)
- `main_title` / `subtitle`: text shown at the top
- `duration`: 5–7 seconds (default 5)
- `fade_in`: 1.5–2 seconds (default 1.5)
- `response_format`: `url` (uploads to R2 `outfits/`) or `binary`

**Response**:
```json
{
  "status": "success",
  "message": "Outfit video created successfully",
  "filename": "outfit_<uuid>.mp4",
  "download_url": "https://<bucket>.r2.dev/outfits/outfit_<uuid>.mp4",
  "processing_time": 1.8
}
```

### 4. Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

## Style Templates

### Default
- **Font**: Inter Regular, 48px
- **Colors**: White text, black border (2px)
- **Position**: Center
- **Effects**: Shadow, semi-transparent background

### Bold
- **Font**: Inter Bold, 56px
- **Colors**: White text, black border (3px)
- **Position**: Center
- **Effects**: Stronger shadow, darker background

### Minimal
- **Font**: Inter Regular, 40px
- **Colors**: White text, no border
- **Position**: Center
- **Effects**: Light shadow only

### Cinematic
- **Font**: Inter Bold, 64px
- **Colors**: White text, black border (3px)
- **Position**: Bottom center
- **Effects**: Strong shadow, dark background

## Customization Options

### Override Parameters

```json
{
  "overrides": {
    "font_family": "bold",              // "regular" | "bold"
    "font_size": 64,                    // 12-200
    "text_color": "#FFFFFF",            // hex or named
    "border_width": 3,                  // 0-10
    "border_color": "black",
    "shadow_x": 5,                      // -20 to 20
    "shadow_y": 5,                      // -20 to 20
    "shadow_color": "black",
    "background_enabled": true,
    "background_color": "black",
    "background_opacity": 0.5,          // 0.0-1.0
    "text_opacity": 1.0,                // 0.0-1.0
    "position": "center",               // see positions below
    "custom_x": 100,                    // for "custom" position
    "custom_y": 100,                    // for "custom" position
    "alignment": "center"               // "left" | "center" | "right"
  }
}
```

### Position Options

- `center` - Centered in frame
- `top-left` - Top left corner (10px padding)
- `top-right` - Top right corner
- `top-center` - Top center
- `bottom-left` - Bottom left corner
- `bottom-right` - Bottom right corner
- `bottom-center` - Bottom center
- `middle-left` - Middle left edge
- `middle-right` - Middle right edge
- `custom` - Use custom_x and custom_y coordinates

### Supported Colors

**Named Colors**: white, black, red, green, blue, yellow, cyan, magenta, orange, purple, pink, gray

**Hex Colors**: `#FF0000`, `#00FF00`, etc.

## Python Client Example

```python
import requests

# Process from URL
response = requests.post(
    "https://your-api.railway.app/overlay/url",
    json={
        "url": "https://your-bucket.r2.dev/video.mp4",
        "text": "Amazing Video",
        "template": "cinematic",
        "overrides": {
            "font_size": 72,
            "text_color": "#FFD700",
            "position": "bottom-center"
        }
    }
)

# Save result
with open("output.mp4", "wb") as f:
    f.write(response.content)
```

## JavaScript/TypeScript Example

```typescript
// Process from URL
const response = await fetch('https://your-api.railway.app/overlay/url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://your-bucket.r2.dev/video.mp4',
    text: 'Amazing Video',
    template: 'cinematic',
    overrides: {
      font_size: 72,
      text_color: '#FFD700',
      position: 'bottom-center'
    }
  })
});

const blob = await response.blob();
const url = URL.createObjectURL(blob);
// Use url for download or preview
```

## Railway Deployment

### One-Click Deploy

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects the Dockerfile and deploys

3. **Configure Environment** (Optional):
```bash
# In Railway dashboard, add environment variables:
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_TIMEOUT=30
```

4. **Get Your API URL**:
   - Railway provides a public URL: `https://your-project.railway.app`
   - Use this as your API endpoint

### Enable R2 Upload (Optional)

To enable automatic upload of processed files to R2:

1. **Add to Railway Environment Variables**:
```bash
R2_ENABLED=true
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
```

2. **Uncomment boto3 in requirements.txt**:
```txt
boto3==1.29.7
botocore==1.32.7
```

3. **Redeploy** - Railway will rebuild with R2 support

## File Specifications

### Supported Formats

**Images**: JPG, JPEG, PNG
**Videos**: MP4, MOV, AVI

### Size Limits

- **Max file size**: 100MB (configurable via `MAX_FILE_SIZE` env var)
- **Download timeout**: 30 seconds (configurable via `UPLOAD_TIMEOUT`)
- **Processing timeout**: 2 minutes per file

### Output Formats

- `same` - Keep original format (default)
- `mp4` - Convert to MP4 (videos)
- `jpg` - Convert to JPG (images)
- `png` - Convert to PNG (images)

## Architecture

```
ffmpeg-scripts/
├── main.py                 # FastAPI application
├── config.py              # Configuration & templates
├── services/
│   ├── ffmpeg_service.py  # FFmpeg processing
│   ├── download_service.py # URL downloads
│   └── storage_service.py # R2 integration
├── models/
│   └── schemas.py         # Pydantic models
├── fonts/                 # Inter font files
├── temp/                  # Temporary processing
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
└── railway.toml          # Railway config
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port (auto-set by Railway) |
| `MAX_FILE_SIZE` | 104857600 | Max file size in bytes (100MB) |
| `UPLOAD_TIMEOUT` | 30 | URL download timeout in seconds |
| `R2_ENABLED` | false | Enable R2 storage |
| `R2_ACCOUNT_ID` | - | Cloudflare account ID |
| `R2_ACCESS_KEY_ID` | - | R2 access key |
| `R2_SECRET_ACCESS_KEY` | - | R2 secret key |
| `R2_BUCKET_NAME` | - | R2 bucket name |

## Troubleshooting

### FFmpeg Not Found
```bash
# Ensure FFmpeg is installed
ffmpeg -version

# On Docker, it's included automatically
```

### Font Issues
```bash
# Check font availability
fc-list | grep Inter

# Download fonts to fonts/ directory
# Docker automatically downloads Inter font
```

### Memory Issues
- Reduce `MAX_FILE_SIZE` for Railway's memory limits
- Process smaller files or upgrade Railway plan

### Timeout Errors
- Increase `UPLOAD_TIMEOUT` for large files
- Use faster storage (R2 is optimized for this)

## Performance Tips

1. **Use URL endpoint** - Faster than uploads, especially on Railway
2. **Keep files on R2** - Minimize data transfer
3. **Optimize video settings** - Use MP4 with H.264 for best compatibility
4. **Enable R2 upload** - Return URLs instead of files for faster response

## Security

- Input validation with Pydantic
- Command injection prevention
- File type restrictions
- Size limits
- Non-root Docker user
- CORS configuration (configure for production)

## License

MIT License - Use freely in your projects

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ffmpeg-scripts/issues)
- **Docs**: http://localhost:8000/docs (interactive API documentation)
- **Railway Docs**: https://docs.railway.app

---

Built with FastAPI, FFmpeg, and Inter font. Optimized for Railway deployment.

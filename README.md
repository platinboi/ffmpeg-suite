# FFmpeg Suite API

A production-ready FastAPI service for video/image processing. Includes text overlays, collage generation, and AI background removal.

**Base URL**: `https://ffmpeg-suite-production.up.railway.app`

## Authentication

All endpoints (except `/health`, `/docs`, `/templates`) require an API key:

```
X-API-Key: your_api_key_here
```

Or use Bearer token:
```
Authorization: Bearer your_api_key_here
```

---

## Endpoints Reference

### 1. Health Check

**GET /health**

Check if the service is running and dependencies are available.

**Response:**
```json
{
  "status": "healthy",
  "ffmpeg_available": true,
  "fonts_available": true,
  "version": "1.0.0"
}
```

---

### 2. Background Removal

**POST /rembg**

Remove the background from an image using AI. Returns a transparent PNG.

**Request Body:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_url` | string | *required* | URL of the image to process |
| `response_format` | string | `"url"` | `"url"` returns R2 link, `"binary"` returns file |
| `folder` | string | `"rembg"` | R2 folder for storage (alphanumeric, hyphens, underscores) |
| `model` | string | `"u2net"` | AI model to use (see models below) |
| `alpha_matting` | boolean | `false` | Enable edge refinement for cleaner cutouts |
| `foreground_threshold` | integer | `240` | 0-255. Pixels with alpha above this are kept as foreground |
| `background_threshold` | integer | `10` | 0-255. Pixels with alpha below this are removed as background |
| `erode_size` | integer | `10` | 0-50. Amount of edge erosion applied during alpha matting |
| `post_process_mask` | boolean | `false` | Apply smoothing to the segmentation mask edges |
| `bgcolor` | array | `null` | RGBA array like `[255,255,255,255]` to replace transparency with solid color. Leave null for transparent output. |

**Available Models** (from [rembg](https://github.com/danielgatis/rembg)):

| Model | Description | Best For |
|-------|-------------|----------|
| `u2net` | General purpose model (~170MB) | Default, works well for most cases |
| `u2netp` | Lightweight u2net variant | Faster processing, slightly lower quality |
| `u2net_human_seg` | Trained for human segmentation | People, portraits |
| `u2net_cloth_seg` | Clothing parser | Separating clothing from background |
| `silueta` | Compressed u2net (~43MB) | Memory-constrained environments |
| `isnet-general-use` | Modern general-purpose model | Alternative to u2net, often better edges |
| `isnet-anime` | Anime character segmentation | Anime, cartoon, illustrated content |
| `birefnet-general` | High quality BiRefNet model | Best quality, slower |
| `birefnet-general-lite` | Lightweight BiRefNet | Balance of quality and speed |
| `birefnet-portrait` | Portrait-optimized BiRefNet | Human portraits, headshots |
| `birefnet-massive` | Trained on massive dataset | Complex scenes |

**Example Request:**
```bash
curl -X POST "https://ffmpeg-suite-production.up.railway.app/rembg" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "response_format": "url",
    "folder": "product_images",
    "model": "isnet-general-use",
    "alpha_matting": true
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Background removed successfully",
  "filename": "rembg_abc123.png",
  "download_url": "https://storage.example.com/product_images/rembg_abc123.png",
  "processing_time": 2.5
}
```

---

### 3. Outfit Collage Video

**POST /outfit**

Generate a 9:16 video with 9 product images in a 3x3 grid layout, with title and subtitle text.

**Request Body:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_urls` | array | *required* | Exactly 9 image URLs (JPG/PNG) |
| `main_title` | string | `"Choose your outfit:"` | Title text at top (1-200 chars) |
| `subtitle` | string | `"shop in bio"` | Subtitle text (0-200 chars) |
| `title_font_size` | integer | `74` | Title font size (40-120) |
| `subtitle_font_size` | integer | `40` | Subtitle font size (30-110) |
| `duration` | float | `6.0` | Video duration in seconds (5.0-7.0) |
| `fade_in` | float | `null` | Fade-in duration (2.5-3.0). If null, randomized within range |
| `response_format` | string | `"url"` | `"url"` or `"binary"` |

**Example Request:**
```bash
curl -X POST "https://ffmpeg-suite-production.up.railway.app/outfit" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
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
    "duration": 6,
    "response_format": "url"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Outfit video created successfully",
  "filename": "outfit_abc123.mp4",
  "download_url": "https://storage.example.com/outfits/outfit_abc123.mp4",
  "processing_time": 8.5
}
```

---

### 4. POV Collage Video

**POST /pov**

Generate a 9:16 video with 8 images in a specific "POV" layout with overlapping elements.

**Request Body:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `images` | object | *required* | Object with 8 named image slots (see below) |
| `main_title` | string | `"POV: me and the boys..."` | Title in black header (1-200 chars) |
| `subtitle` | string | `"(clothes in bio)"` | Subtitle on white body (0-200 chars) |
| `title_font_size` | integer | `66` | Title font size (48-120) |
| `subtitle_font_size` | integer | `38` | Subtitle font size (26-90) |
| `duration` | float | `6.0` | Video duration in seconds (5.0-7.0) |
| `fade_in` | float | `null` | Fade-in duration (2.5-3.0). If null, randomized |
| `response_format` | string | `"url"` | `"url"` or `"binary"` |

**Required Image Slots:**

| Slot | Position | Description |
|------|----------|-------------|
| `cap` | Top-left | Hat/cap image |
| `flag` | Upper-middle | Flag or banner |
| `landscape` | Large right | Main landscape/scene |
| `shirt` | Mid-left | Shirt/top |
| `watch` | Center overlay | Watch/accessory |
| `pants` | Lower-left | Pants/bottoms |
| `shoes` | Over pants | Footwear |
| `car` | Lower-right | Vehicle/transport |

**Example Request:**
```bash
curl -X POST "https://ffmpeg-suite-production.up.railway.app/pov" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{
    "images": {
      "cap": "https://example.com/cap.jpg",
      "flag": "https://example.com/flag.jpg",
      "landscape": "https://example.com/landscape.jpg",
      "shirt": "https://example.com/shirt.jpg",
      "watch": "https://example.com/watch.jpg",
      "pants": "https://example.com/pants.jpg",
      "shoes": "https://example.com/shoes.jpg",
      "car": "https://example.com/car.jpg"
    },
    "main_title": "POV: weekend vibes",
    "subtitle": "(shop in bio)",
    "response_format": "url"
  }'
```

---

### 5. Text Overlay from URL

**POST /overlay/url**

Add text overlay to an image or video from a URL.

**Request Body:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | *required* | URL of image/video to process |
| `text` | string | *required* | Text to overlay (1-500 chars) |
| `template` | string | `"default"` | Template name to use |
| `overrides` | object | `null` | Override specific style settings (see below) |
| `output_format` | string | `"same"` | `"same"`, `"mp4"`, `"jpg"`, or `"png"` |
| `response_format` | string | `"binary"` | `"url"` or `"binary"` |

**Override Options:**

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `font_size` | integer | 12-200 | Text size in pixels |
| `font_weight` | integer | 100-900 | Font weight (400=regular, 700=bold) |
| `text_color` | string | - | Hex (`#FFFFFF`) or named color |
| `border_width` | integer | 0-10 | Text outline width |
| `border_color` | string | - | Outline color |
| `shadow_x` | integer | -20 to 20 | Shadow horizontal offset |
| `shadow_y` | integer | -20 to 20 | Shadow vertical offset |
| `shadow_color` | string | - | Shadow color |
| `background_enabled` | boolean | - | Show background box behind text |
| `background_color` | string | - | Background box color |
| `background_opacity` | float | 0.0-1.0 | Background transparency |
| `text_opacity` | float | 0.0-1.0 | Text transparency |
| `position` | string | - | Text position (see positions below) |
| `custom_x` | integer | 0+ | X coordinate for custom position |
| `custom_y` | integer | 0+ | Y coordinate for custom position |
| `alignment` | string | - | `"left"`, `"center"`, or `"right"` |
| `max_text_width_percent` | integer | 10-100 | Max text width as % of frame |
| `line_spacing` | integer | -50 to 50 | Space between lines (negative = tighter) |

**Position Options:**
`center`, `top-left`, `top-right`, `top-center`, `bottom-left`, `bottom-right`, `bottom-center`, `middle-left`, `middle-right`, `custom`

**Named Colors:**
`white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `orange`, `purple`, `pink`, `gray`

**Example Request:**
```bash
curl -X POST "https://ffmpeg-suite-production.up.railway.app/overlay/url" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{
    "url": "https://example.com/video.mp4",
    "text": "Amazing Content",
    "template": "default",
    "overrides": {
      "font_size": 64,
      "text_color": "#FFFFFF",
      "position": "bottom-center"
    },
    "response_format": "url"
  }'
```

---

### 6. Text Overlay from Upload

**POST /overlay/upload**

Add text overlay to an uploaded image or video file.

**Form Data:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | file | *required* | Image or video file |
| `text` | string | *required* | Text to overlay (1-500 chars) |
| `template` | string | `"default"` | Template name |
| `overrides` | string | `null` | JSON string of override options |
| `output_format` | string | `"same"` | Output format |
| `response_format` | string | `"binary"` | `"url"` or `"binary"` |

**Example Request:**
```bash
curl -X POST "https://ffmpeg-suite-production.up.railway.app/overlay/upload" \
  -H "X-API-Key: your_key" \
  -F "file=@video.mp4" \
  -F "text=Hello World" \
  -F "template=default" \
  -F 'overrides={"font_size": 72, "position": "center"}'
```

---

### 7. Merge Clips

**POST /overlay/merge**

Merge 2-10 video clips with individual text overlays into a single video.

**Request Body:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clips` | array | *required* | Array of 2-10 clip configurations |
| `output_format` | string | `"mp4"` | `"mp4"` or `"mov"` |
| `response_format` | string | `"binary"` | `"url"` or `"binary"` |
| `first_clip_duration` | float | `null` | Trim first clip to this duration (0-300 seconds) |
| `first_clip_trim_mode` | string | `"both"` | `"start"`, `"end"`, or `"both"` |

**Clip Configuration:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | Video URL |
| `text` | string | Text overlay for this clip |
| `template` | string | Template name |
| `overrides` | object | Style overrides |

**Example Request:**
```bash
curl -X POST "https://ffmpeg-suite-production.up.railway.app/overlay/merge" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{
    "clips": [
      {"url": "https://example.com/clip1.mp4", "text": "Part 1"},
      {"url": "https://example.com/clip2.mp4", "text": "Part 2"}
    ],
    "output_format": "mp4",
    "response_format": "url"
  }'
```

---

### 8. Templates

**GET /templates** - List all templates

**GET /templates/{name}** - Get specific template

**POST /templates** - Create new template

**PUT /templates/{name}** - Update template

**DELETE /templates/{name}** - Delete template

**POST /templates/{name}/duplicate** - Duplicate template

**Template Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Template identifier (1-100 chars) |
| `font_size` | integer | Text size (12-200) |
| `font_weight` | integer | Font weight (100-900) |
| `text_color` | string | Text color |
| `border_width` | integer | Outline width (0-10) |
| `border_color` | string | Outline color |
| `shadow_x` | integer | Shadow X offset (-20 to 20) |
| `shadow_y` | integer | Shadow Y offset (-20 to 20) |
| `shadow_color` | string | Shadow color |
| `position` | string | Text position |
| `background_enabled` | boolean | Show background box |
| `background_color` | string | Background color |
| `background_opacity` | float | Background transparency (0-1) |
| `text_opacity` | float | Text transparency (0-1) |
| `alignment` | string | Text alignment |
| `max_text_width_percent` | integer | Max width % (10-100) |
| `line_spacing` | integer | Line spacing (-50 to 50) |

---

## File Specifications

**Supported Input Formats:**
- Images: JPG, JPEG, PNG
- Videos: MP4, MOV, AVI

**Limits:**
- Max file size: 100MB
- Max text length: 500 characters
- Processing timeout: 2 minutes

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `MAX_FILE_SIZE` | `104857600` | Max file size in bytes (100MB) |
| `R2_ENABLED` | `false` | Enable Cloudflare R2 storage |
| `R2_ACCOUNT_ID` | - | Cloudflare account ID |
| `R2_ACCESS_KEY_ID` | - | R2 access key |
| `R2_SECRET_ACCESS_KEY` | - | R2 secret key |
| `R2_BUCKET_NAME` | - | R2 bucket name |

---

## Error Responses

All errors return:
```json
{
  "status": "error",
  "message": "Description of what went wrong"
}
```

**Common HTTP Status Codes:**
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (missing/invalid API key)
- `413` - File too large
- `500` - Server error
- `503` - Storage not enabled

---

## Rate Limits

No hard rate limits, but recommended:
- Background removal: 0.5s delay between requests
- Video processing: Sequential processing recommended

---

Built with FastAPI, FFmpeg, and [rembg](https://github.com/danielgatis/rembg).

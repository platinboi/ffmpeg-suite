# API Curl Examples

## Generated API Key
```
sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U
```

---

## 1. Merge Two Clips with Text Overlays (Default Template)

This merges 2 video clips with text overlays using the default template:

```bash
curl -X POST http://localhost:8000/overlay/merge \
  -H "X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U" \
  -H "Content-Type: application/json" \
  -d '{
    "clips": [
      {
        "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "text": "First Clip - For Bigger Blazes",
        "template": "default"
      },
      {
        "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "text": "Second Clip - For Bigger Escapes",
        "template": "default"
      }
    ],
    "output_format": "mp4"
  }' \
  --output merged_output.mp4
```

---

## 2. Merge with Custom Text Overrides

Merge clips with custom font sizes, colors, and positions:

```bash
curl -X POST http://localhost:8000/overlay/merge \
  -H "X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U" \
  -H "Content-Type: application/json" \
  -d '{
    "clips": [
      {
        "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "text": "CLIP ONE",
        "template": "default",
        "overrides": {
          "font_size": 72,
          "text_color": "#FF0000",
          "position": "top-center",
          "border_width": 5,
          "border_color": "#000000"
        }
      },
      {
        "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "text": "CLIP TWO",
        "template": "default",
        "overrides": {
          "font_size": 72,
          "text_color": "#00FF00",
          "position": "bottom-center",
          "background_enabled": true,
          "background_color": "#000000",
          "background_opacity": 0.7
        }
      }
    ],
    "output_format": "mp4"
  }' \
  --output merged_custom.mp4
```

---

## 3. Test Shorter Clips (Faster Testing)

Using shorter test clips for faster testing:

```bash
curl -X POST http://localhost:8000/overlay/merge \
  -H "X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U" \
  -H "Content-Type: application/json" \
  -d '{
    "clips": [
      {
        "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
        "text": "Big Buck Bunny - Part 1",
        "template": "default"
      },
      {
        "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
        "text": "Big Buck Bunny - Part 2",
        "template": "default"
      }
    ],
    "output_format": "mp4"
  }' \
  --output test_merge.mp4
```

---

## 4. Single Clip Overlay (Not Merge)

If you just want to add text to a single clip:

```bash
curl -X POST http://localhost:8000/overlay/url \
  -H "X-API-Key: sk_live__YDMB_zH4YiBXZClpEUWSz6iULklvvg-BWTcMOw2t4U" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "text": "Single Clip Test",
    "template": "default",
    "output_format": "mp4"
  }' \
  --output single_clip.mp4
```

---

## Template Management (No Auth Required)

### List Available Templates
```bash
curl http://localhost:8000/templates | python -m json.tool
```

### Get Specific Template
```bash
curl http://localhost:8000/templates/default | python -m json.tool
```

### Create New Template
```bash
curl -X POST http://localhost:8000/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_custom",
    "font_size": 64,
    "font_weight": 600,
    "text_color": "#FFFF00",
    "border_width": 4,
    "border_color": "#000000",
    "shadow_x": 2,
    "shadow_y": 2,
    "shadow_color": "#000000",
    "position": "center",
    "background_enabled": true,
    "background_color": "#000000",
    "background_opacity": 0.5,
    "text_opacity": 1.0,
    "alignment": "center",
    "max_text_width_percent": 80
  }' | python -m json.tool
```

### Delete Template
```bash
curl -X DELETE http://localhost:8000/templates/my_custom
```

---

## Notes

- **API is running on:** http://localhost:8000
- **UI is running on:** http://localhost:3000
- **OpenAPI docs:** http://localhost:8000/docs
- **No duration limits** - Merge any length videos (only timeout is 10 minutes processing)
- **Max 10 clips per merge request**
- **Max 500 characters per text overlay**
- Template endpoints do NOT require authentication
- Overlay/Merge endpoints REQUIRE API key authentication

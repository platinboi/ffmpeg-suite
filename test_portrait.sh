#!/bin/bash

echo "========================================="
echo "Portrait (9:16) Test Suite"
echo "========================================="
echo ""

BASE_URL="http://localhost:8000"

# Test 1: Default Template
echo "✓ Test 1: Default Template (Center)"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.png" \
  -F "text=Default Style" \
  -F "template=default" \
  --output portrait_default.png
echo "Saved: portrait_default.png ($(ls -lh portrait_default.png | awk '{print $5}'))"
echo ""

# Test 2: Bold Template
echo "✓ Test 2: Bold Template (Center)"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.png" \
  -F "text=BOLD TEXT" \
  -F "template=bold" \
  --output portrait_bold.png
echo "Saved: portrait_bold.png ($(ls -lh portrait_bold.png | awk '{print $5}'))"
echo ""

# Test 3: Minimal Template
echo "✓ Test 3: Minimal Template (Center)"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.png" \
  -F "text=Minimal Clean" \
  -F "template=minimal" \
  --output portrait_minimal.png
echo "Saved: portrait_minimal.png ($(ls -lh portrait_minimal.png | awk '{print $5}'))"
echo ""

# Test 4: Cinematic Template (Bottom Center)
echo "✓ Test 4: Cinematic Template (Bottom Center)"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.png" \
  -F "text=CINEMATIC" \
  -F "template=cinematic" \
  --output portrait_cinematic.png
echo "Saved: portrait_cinematic.png ($(ls -lh portrait_cinematic.png | awk '{print $5}'))"
echo ""

# Test 5: Top Center Position
echo "✓ Test 5: Custom - Top Center"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.png" \
  -F "text=TOP CENTER" \
  -F "template=bold" \
  -F 'overrides={"position": "top-center"}' \
  --output portrait_top.png
echo "Saved: portrait_top.png ($(ls -lh portrait_top.png | awk '{print $5}'))"
echo ""

# Test 6: Bottom Center Position
echo "✓ Test 6: Custom - Bottom Center"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.png" \
  -F "text=BOTTOM CENTER" \
  -F "template=bold" \
  -F 'overrides={"position": "bottom-center"}' \
  --output portrait_bottom.png
echo "Saved: portrait_bottom.png ($(ls -lh portrait_bottom.png | awk '{print $5}'))"
echo ""

# Test 7: Gold Color Custom
echo "✓ Test 7: Custom - Gold Color, Large Font"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.png" \
  -F "text=GOLD STYLE" \
  -F "template=default" \
  -F 'overrides={"text_color": "#FFD700", "font_size": 90, "border_width": 5}' \
  --output portrait_gold.png
echo "Saved: portrait_gold.png ($(ls -lh portrait_gold.png | awk '{print $5}'))"
echo ""

# Test 8: Portrait Video
echo "✓ Test 8: Portrait Video - Cinematic"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.mp4" \
  -F "text=AMAZING STORY" \
  -F "template=cinematic" \
  --output portrait_video.mp4
echo "Saved: portrait_video.mp4 ($(ls -lh portrait_video.mp4 | awk '{print $5}'))"
echo ""

# Test 9: Multi-line text
echo "✓ Test 9: Multi-line Text"
curl -s -X POST "$BASE_URL/overlay/upload" \
  -F "file=@portrait_test.png" \
  -F "text=DOUBLE LINE" \
  -F "template=bold" \
  -F 'overrides={"position": "middle-left"}' \
  --output portrait_multiline.png
echo "Saved: portrait_multiline.png ($(ls -lh portrait_multiline.png | awk '{print $5}'))"
echo ""

echo "========================================="
echo "All Portrait Tests Complete!"
echo "========================================="
echo ""
echo "Generated files:"
ls -lh portrait_*.png portrait_*.mp4 2>/dev/null
echo ""
echo "Moving test files to tests/ folder..."
mv portrait_*.png portrait_*.mp4 tests/ 2>/dev/null
echo "Done! Files moved to tests/ folder"

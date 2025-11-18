#!/bin/bash

echo "========================================="
echo "Clean Templates Test Suite"
echo "========================================="
echo ""

# Test 1: Clean template - Portrait
echo "✓ Test 1: Clean (Portrait 9:16)"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait_test.png \
  -F text="Clean Portrait" \
  -F template=clean \
  --output clean_portrait.png
echo "Saved: clean_portrait.png"

# Test 2: Clean Bold - Portrait
echo "✓ Test 2: Clean Bold (Portrait 9:16)"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait_test.png \
  -F text="Bold Portrait" \
  -F template=clean-bold \
  --output clean_bold_portrait.png
echo "Saved: clean_bold_portrait.png"

# Test 3: Clean Minimal - Portrait
echo "✓ Test 3: Clean Minimal (Portrait 9:16)"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait_test.png \
  -F text="Minimal Clean" \
  -F template=clean-minimal \
  --output clean_minimal_portrait.png
echo "Saved: clean_minimal_portrait.png"

# Create landscape test file
echo ""
echo "Creating landscape test file (1920x1080)..."
ffmpeg -f lavfi -i color=c=teal:s=1920x1080:d=1 -frames:v 1 -y landscape_test.png 2>&1 | tail -1

# Test 4: Clean - Landscape
echo "✓ Test 4: Clean (Landscape 16:9)"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@landscape_test.png \
  -F text="Clean Landscape" \
  -F template=clean \
  --output clean_landscape.png
echo "Saved: clean_landscape.png"

# Test 5: Clean Bold - Landscape
echo "✓ Test 5: Clean Bold (Landscape 16:9)"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@landscape_test.png \
  -F text="Bold Landscape" \
  -F template=clean-bold \
  --output clean_bold_landscape.png
echo "Saved: clean_bold_landscape.png"

# Test 6: Video with clean template
echo "✓ Test 6: Portrait Video - Clean"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait_test.mp4 \
  -F text="Amazing Story" \
  -F template=clean \
  --output clean_video.mp4
echo "Saved: clean_video.mp4"

echo ""
echo "========================================="
echo "Clean Templates Test Complete!"
echo "========================================="
echo ""
ls -lh clean_*.png clean_*.mp4 2>/dev/null

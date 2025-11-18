#!/bin/bash

echo "========================================="
echo "Final Clean Template Test Suite"
echo "========================================="
echo ""

# Portrait Tests
echo "📱 PORTRAIT TESTS (9:16)"
echo "---"

echo "1. Clean Template"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait.png \
  -F text="Hello World" \
  -F template=clean \
  --output test_portrait_clean.png
echo "   ✓ test_portrait_clean.png"

echo "2. Clean Bold Template"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait.png \
  -F text="Bold Portrait" \
  -F template=clean-bold \
  --output test_portrait_bold.png
echo "   ✓ test_portrait_bold.png"

echo "3. Clean Minimal Template"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait.png \
  -F text="Minimal Style" \
  -F template=clean-minimal \
  --output test_portrait_minimal.png
echo "   ✓ test_portrait_minimal.png"

echo ""
echo "🖥️  LANDSCAPE TESTS (16:9)"
echo "---"

echo "4. Clean Template"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@landscape.png \
  -F text="Landscape View" \
  -F template=clean \
  --output test_landscape_clean.png
echo "   ✓ test_landscape_clean.png"

echo "5. Clean Bold Template"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@landscape.png \
  -F text="Bold Landscape" \
  -F template=clean-bold \
  --output test_landscape_bold.png
echo "   ✓ test_landscape_bold.png"

echo "6. Clean Minimal Template"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@landscape.png \
  -F text="Clean & Simple" \
  -F template=clean-minimal \
  --output test_landscape_minimal.png
echo "   ✓ test_landscape_minimal.png"

echo ""
echo "🎬 VIDEO TEST"
echo "---"

echo "7. Portrait Video - Clean"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait.mp4 \
  -F text="Amazing Story" \
  -F template=clean \
  --output test_video_clean.mp4
echo "   ✓ test_video_clean.mp4"

echo ""
echo "🎨 TEXT VARIATION TESTS"
echo "---"

echo "8. Longer Text"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait.png \
  -F text="This is a Longer Text Example" \
  -F template=clean-bold \
  --output test_long_text.png
echo "   ✓ test_long_text.png"

echo "9. Short Text"
curl -s -X POST http://localhost:8000/overlay/upload \
  -F file=@portrait.png \
  -F text="Hi!" \
  -F template=clean \
  --output test_short_text.png
echo "   ✓ test_short_text.png"

echo ""
echo "========================================="
echo "✅ All Tests Complete!"
echo "========================================="
echo ""
echo "Generated files:"
ls -lh test_*.png test_*.mp4
echo ""
echo "Moving to tests/ folder..."
mv test_*.png test_*.mp4 tests/ 2>/dev/null
echo "✓ Done!"

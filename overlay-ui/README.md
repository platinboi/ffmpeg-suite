# Text Overlay Editor

A modern Next.js application for adding text overlays to images and videos with real-time preview.

## Features

- **File Upload & URL Input**: Upload files or paste URLs to process images/videos
- **Real-time Canvas Preview**: See changes instantly without calling FFmpeg
- **Comprehensive Text Controls**:
  - Text input with multiline support
  - Font size (20-150px)
  - Text alignment (left, center, right)
  - Text color with color picker
- **Advanced Styling**:
  - Border width and color
  - Shadow with X/Y offsets and color
  - Background box with opacity control
- **Flexible Positioning**:
  - 9 preset positions (corners, edges, center)
  - Fine-tune with X/Y offset sliders (±150px)
- **Modern UI**: Clean, minimalistic design with card-based sections

## Tech Stack

- **Next.js 16** with App Router
- **React 19** with TypeScript
- **Tailwind CSS 3.4.1** for styling
- **Zustand** for state management
- **Lucide React** for icons
- **React Colorful** for color picking
- **React Dropzone** for file uploads

## Getting Started

1. **Install dependencies**:
```bash
npm install
```

2. **Start the development server**:
```bash
npm run dev
```

3. **Open the app**: Navigate to [http://localhost:3000](http://localhost:3000)

## Environment Variables

Create a `.env.local` file:

```env
FFMPEG_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture

### Next.js API Routes
- `/api/overlay/upload` - Proxy to FFmpeg backend for file uploads
- `/api/overlay/url` - Proxy to FFmpeg backend for URL processing
- `/api/health` - Health check endpoint
- `/api/templates` - Get available templates

### Benefits of Next.js API Routes
- **No CORS issues**: Frontend and backend on same origin
- **Simplified deployment**: Single application
- **Better security**: Hide backend URL from client
- **Future-ready**: Easy to add authentication with NextAuth.js

## Fixed Bugs from Vite Version

1. **Position Calculation**: Fixed double-addition of offsets in preview canvas
2. **API Integration**: Position offsets now properly sent to backend
3. **CORS Issues**: Eliminated by using Next.js API routes
4. **Image Loading**: Proper handling of both images and videos from URLs

## Project Structure

```
overlay-ui/
├── app/
│   ├── api/              # Next.js API routes
│   ├── globals.css       # Global styles
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Main editor page
├── components/
│   ├── controls/         # Control components
│   ├── file-input-tabs.tsx
│   ├── file-upload-zone.tsx
│   ├── preview-canvas.tsx
│   └── url-input.tsx
└── lib/
    ├── api.ts            # API client
    ├── store.ts          # Zustand store
    ├── types.ts          # TypeScript types
    └── utils.ts          # Utility functions
```

## Usage

1. **Upload or paste URL** of an image or video
2. **Enter text** you want to overlay
3. **Customize style**:
   - Adjust font size
   - Change text color
   - Add border
   - Enable shadow
   - Add background box
4. **Position text**:
   - Select preset position
   - Fine-tune with offset sliders
5. **Click "Generate & Download"** to process and download

## Future Enhancements

- User authentication (NextAuth.js)
- Save/load templates
- Bulk processing queue
- Drag-to-position on canvas
- Font family selector
- Animation support for videos
- Template marketplace

## License

ISC

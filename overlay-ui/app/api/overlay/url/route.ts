import { NextRequest, NextResponse } from 'next/server';

const FFMPEG_API_URL = process.env.FFMPEG_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward the request to the FFmpeg backend
    const response = await fetch(`${FFMPEG_API_URL}/overlay/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { message: error.message || 'Processing failed' },
        { status: response.status }
      );
    }

    // Get the blob from the FFmpeg backend
    const blob = await response.blob();

    // Return the blob with appropriate headers
    return new NextResponse(blob, {
      status: 200,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/octet-stream',
        'Content-Disposition': response.headers.get('Content-Disposition') || 'attachment',
      },
    });
  } catch (error) {
    console.error('URL API error:', error);
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}

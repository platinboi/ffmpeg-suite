import { NextResponse } from 'next/server';

const FFMPEG_API_URL = process.env.FFMPEG_API_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${FFMPEG_API_URL}/health`);

    if (!response.ok) {
      return NextResponse.json(
        { message: 'Backend health check failed' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Health check error:', error);
    return NextResponse.json(
      { message: 'Backend unreachable' },
      { status: 503 }
    );
  }
}

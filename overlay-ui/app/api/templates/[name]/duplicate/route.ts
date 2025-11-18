import { NextRequest, NextResponse } from 'next/server';

const FFMPEG_API_URL = process.env.FFMPEG_API_URL || 'http://localhost:8000';

export async function POST(
  request: NextRequest,
  { params }: { params: { name: string } }
) {
  try {
    const body = await request.json();

    const response = await fetch(
      `${FFMPEG_API_URL}/templates/${params.name}/duplicate`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to duplicate template' },
      { status: 500 }
    );
  }
}

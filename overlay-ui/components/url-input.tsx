'use client';

import { useState } from 'react';
import { Link2, Loader2 } from 'lucide-react';
import { useEditorStore } from '@/lib/store';

export function UrlInput() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const setSourceUrl = useEditorStore((state) => state.setSourceUrl);
  const setFileUrl = useEditorStore((state) => state.setFileUrl);
  const setFileSource = useEditorStore((state) => state.setFileSource);
  const setImageDimensions = useEditorStore((state) => state.setImageDimensions);

  const handleLoad = async () => {
    if (!url) return;

    setLoading(true);
    setError('');

    try {
      // Validate URL
      new URL(url);

      // Store the original URL for backend processing
      setSourceUrl(url);
      setFileSource('url');

      // Use Next.js proxy to avoid CORS issues
      const proxyUrl = `/api/proxy?url=${encodeURIComponent(url)}`;

      // Test the proxied URL
      const response = await fetch(proxyUrl);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to load media from URL');
      }

      const contentType = response.headers.get('content-type') || '';

      // Create a blob URL from the proxied content
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);

      // Set the blob URL for preview (no CORS issues)
      setFileUrl(blobUrl);

      // Determine if it's an image or video and get dimensions
      if (contentType.startsWith('image/')) {
        const img = new Image();
        img.onload = () => {
          setImageDimensions({
            width: img.naturalWidth,
            height: img.naturalHeight,
          });
          setLoading(false);
        };
        img.onerror = () => {
          setError('Failed to load image');
          setLoading(false);
        };
        img.src = blobUrl;
      } else if (contentType.startsWith('video/')) {
        const video = document.createElement('video');
        video.onloadedmetadata = () => {
          setImageDimensions({
            width: video.videoWidth,
            height: video.videoHeight,
          });
          setLoading(false);
        };
        video.onerror = () => {
          setError('Failed to load video');
          setLoading(false);
        };
        video.src = blobUrl;
      } else {
        setError('URL must point to an image or video');
        setLoading(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid URL or failed to load');
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-gray-600">
        <Link2 className="w-4 h-4" />
        <span className="text-sm font-medium">Load from URL</span>
      </div>

      <div className="flex gap-2">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/image.jpg"
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          onKeyPress={(e) => e.key === 'Enter' && handleLoad()}
        />
        <button
          onClick={handleLoad}
          disabled={!url || loading}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white text-sm font-medium rounded-md transition-colors flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading...</span>
            </>
          ) : (
            'Load'
          )}
        </button>
      </div>

      {error && (
        <p className="text-xs text-red-600">{error}</p>
      )}

      <p className="text-xs text-gray-500">
        Paste a direct link to an image or video file
      </p>
    </div>
  );
}

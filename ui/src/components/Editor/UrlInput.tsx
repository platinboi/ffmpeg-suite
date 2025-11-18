import { useState } from 'react';
import { Link2, Loader2 } from 'lucide-react';
import { useEditorStore } from '../../stores/editorStore';

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
      const urlObj = new URL(url);

      // Set the source URL for API processing
      setSourceUrl(url);
      setFileUrl(url);
      setFileSource('url');

      // Load image to get dimensions
      const img = new Image();
      img.crossOrigin = 'anonymous';

      img.onload = () => {
        setImageDimensions({
          width: img.naturalWidth,
          height: img.naturalHeight,
        });
        setLoading(false);
      };

      img.onerror = () => {
        setError('Failed to load image from URL');
        setLoading(false);
      };

      img.src = url;
    } catch (err) {
      setError('Invalid URL format');
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

import { useState } from 'react';
import { Upload, Link2 } from 'lucide-react';
import { ImageUploadZone } from './ImageUploadZone';
import { UrlInput } from './UrlInput';

export function FileInputTabs() {
  const [activeTab, setActiveTab] = useState<'upload' | 'url'>('upload');

  return (
    <div className="w-full max-w-2xl">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('upload')}
          className={`
            flex-1 flex items-center justify-center gap-2 py-3 px-4 font-medium text-sm transition-colors
            ${
              activeTab === 'upload'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }
          `}
        >
          <Upload className="w-4 h-4" />
          Upload File
        </button>
        <button
          onClick={() => setActiveTab('url')}
          className={`
            flex-1 flex items-center justify-center gap-2 py-3 px-4 font-medium text-sm transition-colors
            ${
              activeTab === 'url'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }
          `}
        >
          <Link2 className="w-4 h-4" />
          From URL
        </button>
      </div>

      {/* Content */}
      {activeTab === 'upload' ? <ImageUploadZone /> : <UrlInput />}
    </div>
  );
}

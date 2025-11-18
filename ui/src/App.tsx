import { useState } from 'react';
import { FileInputTabs } from './components/Editor/FileInputTabs';
import { PreviewCanvas } from './components/Editor/PreviewCanvas';
import { TextInput } from './components/Controls/TextInput';
import { FontSizeSlider } from './components/Controls/FontSizeSlider';
import { ColorPicker } from './components/Controls/ColorPicker';
import { PositionPresets } from './components/Editor/PositionPresets';
import { PositionOffsets } from './components/Controls/PositionOffsets';
import { TextAlignment } from './components/Controls/TextAlignment';
import { useEditorStore } from './stores/editorStore';
import { OverlayAPI } from './api/overlay';
import { downloadBlob } from './lib/utils';
import { Loader2, Download, Type, Palette, MapPin } from 'lucide-react';

function App() {
  const file = useEditorStore((state) => state.file);
  const fileUrl = useEditorStore((state) => state.fileUrl);
  const sourceUrl = useEditorStore((state) => state.sourceUrl);
  const fileSource = useEditorStore((state) => state.fileSource);
  const text = useEditorStore((state) => state.text);
  const settings = useEditorStore((state) => state.settings);
  const position = useEditorStore((state) => state.position);
  const updateSetting = useEditorStore((state) => state.updateSetting);

  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!text) return;
    if (fileSource === 'upload' && !file) return;
    if (fileSource === 'url' && !sourceUrl) return;

    setProcessing(true);
    setError(null);

    try {
      let blob: Blob;

      if (fileSource === 'url' && sourceUrl) {
        // Process from URL
        blob = await OverlayAPI.processUrl(sourceUrl, {
          text,
          template: 'default',
          overrides: settings,
        });
      } else if (file) {
        // Process from file upload
        blob = await OverlayAPI.processFile(file, {
          text,
          template: 'default',
          overrides: settings,
        });
      } else {
        return;
      }

      const extension = (file?.type.startsWith('image/') || sourceUrl?.match(/\.(jpg|jpeg|png)$/i)) ? 'png' : 'mp4';
      downloadBlob(blob, `overlay-${Date.now()}.${extension}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed');
      console.error('Processing error:', err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Left Sidebar - Controls */}
      <div className="w-96 bg-white border-r border-gray-200 shadow-sm overflow-y-auto">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="pb-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Text Overlay Editor</h1>
            <p className="text-sm text-gray-500 mt-1">Add text to images & videos</p>
          </div>

          {file ? (
            <>
              {/* Text Section */}
              <div className="space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 text-gray-700 font-medium">
                  <Type className="w-4 h-4" />
                  <span>Text Content</span>
                </div>
                <TextInput />
                <FontSizeSlider />
                <TextAlignment />
              </div>

              {/* Style Section */}
              <div className="space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 text-gray-700 font-medium">
                  <Palette className="w-4 h-4" />
                  <span>Style</span>
                </div>

                <ColorPicker
                  label="Text Color"
                  value={settings.text_color || 'white'}
                  onChange={(color) => updateSetting('text_color', color)}
                />

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <label className="text-sm font-medium text-gray-700">Border Width</label>
                    <span className="text-sm text-gray-500">{settings.border_width || 0}px</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={settings.border_width || 0}
                    onChange={(e) => updateSetting('border_width', Number(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                  />
                </div>

                {(settings.border_width || 0) > 0 && (
                  <ColorPicker
                    label="Border Color"
                    value={settings.border_color || 'black'}
                    onChange={(color) => updateSetting('border_color', color)}
                  />
                )}
              </div>

              {/* Position Section */}
              <div className="space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 text-gray-700 font-medium">
                  <MapPin className="w-4 h-4" />
                  <span>Position</span>
                </div>
                <PositionPresets />
                <PositionOffsets />
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={!text || processing}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-300 text-white font-semibold py-4 px-6 rounded-lg flex items-center justify-center gap-3 transition-all shadow-md hover:shadow-lg disabled:shadow-none"
              >
                {processing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    <span>Generate & Download</span>
                  </>
                )}
              </button>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-700 font-medium">{error}</p>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400">
              <p className="text-sm">Upload a file to get started →</p>
            </div>
          )}
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 flex items-center justify-center p-8">
        {!fileUrl ? (
          <FileInputTabs />
        ) : (
          <div className="relative">
            <PreviewCanvas
              imageUrl={fileUrl}
              text={text}
              settings={settings}
              position={position}
            />
            {text && (
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-500">
                  Preview updates in real-time
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

'use client';

import { useState } from 'react';
import { Loader2, Download, Type, Palette, MapPin, RefreshCw } from 'lucide-react';
import { useEditorStore } from '@/lib/store';
import { OverlayAPI } from '@/lib/api';
import { downloadBlob } from '@/lib/utils';

// Components
import { FileInputTabs } from '@/components/file-input-tabs';
import { PreviewCanvas } from '@/components/preview-canvas';
import { TemplateManager } from '@/components/template-manager';
import { TextInput } from '@/components/controls/text-input';
import { FontSizeSlider } from '@/components/controls/font-size-slider';
import { FontWeightSlider } from '@/components/controls/font-weight-slider';
import { TextWidthControl } from '@/components/controls/text-width-control';
import { ColorPicker } from '@/components/controls/color-picker';
import { TextAlignment } from '@/components/controls/text-alignment';
import { PositionPresets } from '@/components/controls/position-presets';
import { PositionOffsets } from '@/components/controls/position-offsets';
import { ShadowControls } from '@/components/controls/shadow-controls';
import { BackgroundControls } from '@/components/controls/background-controls';
import { SliderWithInput } from '@/components/controls/slider-with-input';

export default function Home() {
  const file = useEditorStore((state) => state.file);
  const fileUrl = useEditorStore((state) => state.fileUrl);
  const sourceUrl = useEditorStore((state) => state.sourceUrl);
  const fileSource = useEditorStore((state) => state.fileSource);
  const text = useEditorStore((state) => state.text);
  const settings = useEditorStore((state) => state.settings);
  const position = useEditorStore((state) => state.position);
  const positionMode = useEditorStore((state) => state.positionMode);
  const updateSetting = useEditorStore((state) => state.updateSetting);
  const reset = useEditorStore((state) => state.reset);

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

      // FIXED: Include position offsets in the settings
      const settingsWithPosition = {
        ...settings,
        // If using custom position mode, send the offsets
        ...(positionMode === 'custom' && {
          position: 'custom',
        }),
      };

      if (fileSource === 'url' && sourceUrl) {
        // Process from URL
        blob = await OverlayAPI.processUrl(sourceUrl, {
          text,
          template: 'default',
          overrides: settingsWithPosition,
        });
      } else if (file) {
        // Process from file upload
        blob = await OverlayAPI.processFile(file, {
          text,
          template: 'default',
          overrides: settingsWithPosition,
        });
      } else {
        return;
      }

      const extension = (file?.type.startsWith('image/') || sourceUrl?.match(/\\.(jpg|jpeg|png)$/i)) ? 'png' : 'mp4';
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

          {fileUrl ? (
            <>
              {/* Template Manager */}
              <TemplateManager />

              {/* Text Section */}
              <div className="space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 text-gray-700 font-medium">
                  <Type className="w-4 h-4" />
                  <span>Text Content</span>
                </div>
                <TextInput />
                <FontSizeSlider />
                <FontWeightSlider />
                <TextWidthControl />
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
                  value={settings.text_color || '#FFFFFF'}
                  onChange={(color) => updateSetting('text_color', color)}
                />

                <SliderWithInput
                  label="Border Width"
                  value={settings.border_width || 0}
                  min={0}
                  max={10}
                  step={1}
                  unit="px"
                  onChange={(value) => updateSetting('border_width', value)}
                />

                {(settings.border_width || 0) > 0 && (
                  <ColorPicker
                    label="Border Color"
                    value={settings.border_color || '#000000'}
                    onChange={(color) => updateSetting('border_color', color)}
                  />
                )}

                <ShadowControls />
                <BackgroundControls />
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
            <div className="absolute top-4 right-4 z-10">
              <button
                onClick={reset}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
                title="Change file and start over"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Change File</span>
              </button>
            </div>
            <PreviewCanvas
              imageUrl={fileUrl}
              text={text}
              settings={settings}
              position={position}
              positionMode={positionMode}
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

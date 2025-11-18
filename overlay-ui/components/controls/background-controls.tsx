'use client';

import { useEditorStore } from '@/lib/store';
import { ColorPicker } from './color-picker';
import { SliderWithInput } from './slider-with-input';

export function BackgroundControls() {
  const settings = useEditorStore((state) => state.settings);
  const updateSetting = useEditorStore((state) => state.updateSetting);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">Background Box</label>
        <button
          onClick={() => updateSetting('background_enabled', !settings.background_enabled)}
          className={`
            px-3 py-1 text-xs font-medium rounded-md transition-colors
            ${
              settings.background_enabled
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }
          `}
        >
          {settings.background_enabled ? 'Enabled' : 'Disabled'}
        </button>
      </div>

      {settings.background_enabled && (
        <>
          <ColorPicker
            label="Background Color"
            value={settings.background_color || '#000000'}
            onChange={(color) => updateSetting('background_color', color)}
          />

          <SliderWithInput
            label="Opacity"
            value={settings.background_opacity || 0}
            min={0}
            max={1}
            step={0.1}
            onChange={(value) => updateSetting('background_opacity', value)}
            formatDisplay={(val) => `${Math.round(val * 100)}%`}
          />
        </>
      )}
    </div>
  );
}

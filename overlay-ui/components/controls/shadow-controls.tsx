'use client';

import { useEditorStore } from '@/lib/store';
import { ColorPicker } from './color-picker';
import { SliderWithInput } from './slider-with-input';

export function ShadowControls() {
  const settings = useEditorStore((state) => state.settings);
  const updateSetting = useEditorStore((state) => state.updateSetting);

  const hasShadow = (settings.shadow_x !== 0 || settings.shadow_y !== 0);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">Shadow</label>
        <button
          onClick={() => {
            if (hasShadow) {
              updateSetting('shadow_x', 0);
              updateSetting('shadow_y', 0);
            } else {
              updateSetting('shadow_x', 2);
              updateSetting('shadow_y', 2);
            }
          }}
          className={`
            px-3 py-1 text-xs font-medium rounded-md transition-colors
            ${
              hasShadow
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }
          `}
        >
          {hasShadow ? 'Enabled' : 'Disabled'}
        </button>
      </div>

      {hasShadow && (
        <>
          <SliderWithInput
            label="Offset X"
            value={settings.shadow_x || 0}
            min={-20}
            max={20}
            step={1}
            unit="px"
            onChange={(value) => updateSetting('shadow_x', value)}
          />

          <SliderWithInput
            label="Offset Y"
            value={settings.shadow_y || 0}
            min={-20}
            max={20}
            step={1}
            unit="px"
            onChange={(value) => updateSetting('shadow_y', value)}
          />

          <ColorPicker
            label="Shadow Color"
            value={settings.shadow_color || '#000000'}
            onChange={(color) => updateSetting('shadow_color', color)}
          />
        </>
      )}
    </div>
  );
}

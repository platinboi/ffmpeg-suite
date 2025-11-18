'use client';

import { useEditorStore } from '@/lib/store';
import { SliderWithInput } from './slider-with-input';

export function FontSizeSlider() {
  const settings = useEditorStore((state) => state.settings);
  const updateSetting = useEditorStore((state) => state.updateSetting);

  return (
    <SliderWithInput
      label="Font Size"
      value={settings.font_size || 54}
      min={20}
      max={150}
      step={1}
      unit="px"
      onChange={(value) => updateSetting('font_size', value)}
    />
  );
}

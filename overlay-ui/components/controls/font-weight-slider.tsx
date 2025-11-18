'use client';

import { useEditorStore } from '@/lib/store';
import { SliderWithInput } from './slider-with-input';

export function FontWeightSlider() {
  const settings = useEditorStore((state) => state.settings);
  const updateSetting = useEditorStore((state) => state.updateSetting);

  const fontWeight = settings.font_weight || 500;

  return (
    <SliderWithInput
      label="Font Weight"
      value={fontWeight}
      min={100}
      max={900}
      step={100}
      onChange={(value) => updateSetting('font_weight', value)}
    />
  );
}

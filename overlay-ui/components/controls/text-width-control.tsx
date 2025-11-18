'use client';

import { useEditorStore } from '@/lib/store';
import { SliderWithInput } from './slider-with-input';

export function TextWidthControl() {
  const settings = useEditorStore((state) => state.settings);
  const updateSetting = useEditorStore((state) => state.updateSetting);

  const maxWidth = settings.max_text_width_percent || 80;

  return (
    <SliderWithInput
      label="Max Text Width"
      value={maxWidth}
      min={10}
      max={100}
      step={5}
      unit="%"
      onChange={(value) => updateSetting('max_text_width_percent', value)}
      formatDisplay={(val) => `${val}% of image width`}
    />
  );
}

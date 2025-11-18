'use client';

import { useEditorStore } from '@/lib/store';
import { SliderWithInput } from './slider-with-input';

export function PositionOffsets() {
  const position = useEditorStore((state) => state.position);
  const setPosition = useEditorStore((state) => state.setPosition);

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-gray-700">Fine Tune Position</label>

      <SliderWithInput
        label="Horizontal"
        value={position.x}
        min={-150}
        max={150}
        step={1}
        unit="px"
        onChange={(value) => setPosition(value, position.y)}
        formatDisplay={(val) => `${val > 0 ? '+' : ''}${val}px`}
      />

      <SliderWithInput
        label="Vertical"
        value={position.y}
        min={-150}
        max={150}
        step={1}
        unit="px"
        onChange={(value) => setPosition(position.x, value)}
        formatDisplay={(val) => `${val > 0 ? '+' : ''}${val}px`}
      />

      <button
        onClick={() => setPosition(0, 0)}
        className="w-full py-1 text-xs text-blue-600 hover:text-blue-700 font-medium"
      >
        Reset Offsets
      </button>
    </div>
  );
}

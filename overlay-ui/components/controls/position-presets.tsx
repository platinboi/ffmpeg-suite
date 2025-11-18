'use client';

import { useEditorStore } from '@/lib/store';

export function PositionPresets() {
  const settings = useEditorStore((state) => state.settings);
  const updateSetting = useEditorStore((state) => state.updateSetting);
  const setPositionMode = useEditorStore((state) => state.setPositionMode);

  const positions = [
    { value: 'top-left', label: 'TL' },
    { value: 'top-center', label: 'TC' },
    { value: 'top-right', label: 'TR' },
    { value: 'middle-left', label: 'ML' },
    { value: 'center', label: 'C' },
    { value: 'middle-right', label: 'MR' },
    { value: 'bottom-left', label: 'BL' },
    { value: 'bottom-center', label: 'BC' },
    { value: 'bottom-right', label: 'BR' },
  ];

  const handlePositionClick = (position: string) => {
    updateSetting('position', position);
    setPositionMode('preset');
  };

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700">Position Preset</label>
      <div className="grid grid-cols-3 gap-2">
        {positions.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => handlePositionClick(value)}
            className={`
              py-3 px-4 text-sm font-medium rounded-md border transition-colors
              ${
                settings.position === value
                  ? 'border-blue-500 bg-blue-50 text-blue-600'
                  : 'border-gray-300 hover:border-gray-400 text-gray-600'
              }
            `}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}

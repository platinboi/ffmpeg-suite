'use client';

import { AlignLeft, AlignCenter, AlignRight } from 'lucide-react';
import { useEditorStore } from '@/lib/store';

export function TextAlignment() {
  const settings = useEditorStore((state) => state.settings);
  const updateSetting = useEditorStore((state) => state.updateSetting);

  const alignment = settings.alignment || 'center';

  const alignments = [
    { value: 'left' as const, icon: AlignLeft, label: 'Left' },
    { value: 'center' as const, icon: AlignCenter, label: 'Center' },
    { value: 'right' as const, icon: AlignRight, label: 'Right' },
  ];

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700">Alignment</label>
      <div className="flex gap-2">
        {alignments.map(({ value, icon: Icon, label }) => (
          <button
            key={value}
            onClick={() => updateSetting('alignment', value)}
            className={`
              flex-1 flex flex-col items-center gap-1 py-2 px-3 rounded-md border transition-colors
              ${
                alignment === value
                  ? 'border-blue-500 bg-blue-50 text-blue-600'
                  : 'border-gray-300 hover:border-gray-400 text-gray-600'
              }
            `}
          >
            <Icon className="w-4 h-4" />
            <span className="text-xs">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

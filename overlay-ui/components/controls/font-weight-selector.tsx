'use client';

import { useEditorStore } from '@/lib/store';

export function FontWeightSelector() {
  const settings = useEditorStore((state) => state.settings);
  const updateSetting = useEditorStore((state) => state.updateSetting);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700">Font Weight</label>
      <div className="flex gap-2">
        <button
          onClick={() => updateSetting('font_family', 'regular')}
          className={`
            flex-1 py-2 px-3 text-sm rounded-md transition-colors
            ${
              settings.font_family !== 'bold'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }
          `}
        >
          Regular
        </button>
        <button
          onClick={() => updateSetting('font_family', 'bold')}
          className={`
            flex-1 py-2 px-3 text-sm font-bold rounded-md transition-colors
            ${
              settings.font_family === 'bold'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }
          `}
        >
          Bold
        </button>
      </div>
    </div>
  );
}

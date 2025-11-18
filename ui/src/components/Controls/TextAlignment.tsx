import { AlignLeft, AlignCenter, AlignRight } from 'lucide-react';
import { useEditorStore } from '../../stores/editorStore';

export function TextAlignment() {
  const alignment = useEditorStore((state) => state.settings.alignment) || 'center';
  const updateSetting = useEditorStore((state) => state.updateSetting);

  const alignments = [
    { value: 'left' as const, icon: AlignLeft, label: 'Left' },
    { value: 'center' as const, icon: AlignCenter, label: 'Center' },
    { value: 'right' as const, icon: AlignRight, label: 'Right' },
  ];

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Text Alignment</label>
      <div className="flex gap-2">
        {alignments.map(({ value, icon: Icon, label }) => (
          <button
            key={value}
            onClick={() => updateSetting('alignment', value)}
            className={`
              flex-1 px-3 py-2 rounded-md border transition-all flex items-center justify-center gap-2
              ${
                alignment === value
                  ? 'bg-blue-500 text-white border-blue-600 shadow-sm'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
              }
            `}
            title={label}
          >
            <Icon className="w-4 h-4" />
            <span className="text-xs font-medium">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

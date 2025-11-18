import { useEditorStore } from '../../stores/editorStore';

const positions = [
  { label: 'Top Left', value: 'top-left' as const },
  { label: 'Top Center', value: 'top-center' as const },
  { label: 'Top Right', value: 'top-right' as const },
  { label: 'Middle Left', value: 'middle-left' as const },
  { label: 'Center', value: 'center' as const },
  { label: 'Middle Right', value: 'middle-right' as const },
  { label: 'Bottom Left', value: 'bottom-left' as const },
  { label: 'Bottom Center', value: 'bottom-center' as const },
  { label: 'Bottom Right', value: 'bottom-right' as const },
];

export function PositionPresets() {
  const currentPosition = useEditorStore((state) => state.settings.position);
  const updateSetting = useEditorStore((state) => state.updateSetting);
  const setPositionMode = useEditorStore((state) => state.setPositionMode);

  const handlePositionChange = (value: string) => {
    updateSetting('position', value);
    setPositionMode('preset');
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Position</label>
      <div className="grid grid-cols-3 gap-2">
        {positions.map((pos) => (
          <button
            key={pos.value}
            onClick={() => handlePositionChange(pos.value)}
            className={`
              px-3 py-2 text-xs font-medium rounded border transition-colors
              ${
                currentPosition === pos.value
                  ? 'bg-blue-500 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
              }
            `}
          >
            {pos.label}
          </button>
        ))}
      </div>
    </div>
  );
}

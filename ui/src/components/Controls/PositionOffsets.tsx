import { useEditorStore } from '../../stores/editorStore';
import { RotateCcw } from 'lucide-react';

export function PositionOffsets() {
  const position = useEditorStore((state) => state.position);
  const setPosition = useEditorStore((state) => state.setPosition);

  const handleReset = () => {
    setPosition(0, 0);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">Fine-tune Position</label>
        <button
          onClick={handleReset}
          className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
          title="Reset offsets"
        >
          <RotateCcw className="w-3 h-3" />
          Reset
        </button>
      </div>

      {/* X Offset */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Horizontal (X)</span>
          <span className="text-gray-500 font-mono">{position.x > 0 ? `+${position.x}` : position.x}px</span>
        </div>
        <input
          type="range"
          min="-150"
          max="150"
          value={position.x}
          onChange={(e) => setPosition(Number(e.target.value), position.y)}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
      </div>

      {/* Y Offset */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Vertical (Y)</span>
          <span className="text-gray-500 font-mono">{position.y > 0 ? `+${position.y}` : position.y}px</span>
        </div>
        <input
          type="range"
          min="-150"
          max="150"
          value={position.y}
          onChange={(e) => setPosition(position.x, Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
      </div>

      <p className="text-xs text-gray-500 italic">
        Adjust from preset position ±150px
      </p>
    </div>
  );
}

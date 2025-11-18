import { useEditorStore } from '../../stores/editorStore';

export function FontSizeSlider() {
  const fontSize = useEditorStore((state) => state.settings.font_size) || 54;
  const updateSetting = useEditorStore((state) => state.updateSetting);

  return (
    <div className="space-y-2">
      <div className="flex justify-between">
        <label className="text-sm font-medium text-gray-700">Font Size</label>
        <span className="text-sm text-gray-500">{fontSize}px</span>
      </div>
      <input
        type="range"
        min="12"
        max="200"
        value={fontSize}
        onChange={(e) => updateSetting('font_size', Number(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
      />
    </div>
  );
}

import { useEditorStore } from '../../stores/editorStore';

export function TextInput() {
  const text = useEditorStore((state) => state.text);
  const setText = useEditorStore((state) => state.setText);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Text</label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter your text here..."
        rows={3}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
      />
      <p className="text-xs text-gray-500">{text.length} / 500 characters</p>
    </div>
  );
}

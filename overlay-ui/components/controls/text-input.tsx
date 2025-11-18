'use client';

import { useEditorStore } from '@/lib/store';

export function TextInput() {
  const text = useEditorStore((state) => state.text);
  const setText = useEditorStore((state) => state.setText);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700">Text</label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter your text here..."
        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[80px] resize-none"
      />
    </div>
  );
}

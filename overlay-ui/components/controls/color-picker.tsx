'use client';

import { useState } from 'react';
import { HexColorPicker } from 'react-colorful';

interface ColorPickerProps {
  label: string;
  value: string;
  onChange: (color: string) => void;
}

export function ColorPicker({ label, value, onChange }: ColorPickerProps) {
  const [showPicker, setShowPicker] = useState(false);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700">{label}</label>
      <div className="relative">
        <button
          onClick={() => setShowPicker(!showPicker)}
          className="w-full flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-md hover:border-gray-400 transition-colors"
        >
          <div
            className="w-6 h-6 rounded border border-gray-300"
            style={{ backgroundColor: value }}
          />
          <span className="text-sm text-gray-700 uppercase">{value}</span>
        </button>
        {showPicker && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setShowPicker(false)}
            />
            <div className="absolute left-0 top-full mt-2 z-20 p-3 bg-white rounded-lg shadow-lg border border-gray-200">
              <HexColorPicker color={value} onChange={onChange} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

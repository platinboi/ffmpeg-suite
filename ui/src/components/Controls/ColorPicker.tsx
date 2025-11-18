import { useState } from 'react';
import { HexColorPicker } from 'react-colorful';
import * as Popover from '@radix-ui/react-popover';

interface ColorPickerProps {
  label: string;
  value: string;
  onChange: (color: string) => void;
}

const namedColors = [
  { name: 'white', hex: '#FFFFFF' },
  { name: 'black', hex: '#000000' },
  { name: 'red', hex: '#FF0000' },
  { name: 'green', hex: '#00FF00' },
  { name: 'blue', hex: '#0000FF' },
  { name: 'yellow', hex: '#FFFF00' },
  { name: 'cyan', hex: '#00FFFF' },
  { name: 'magenta', hex: '#FF00FF' },
];

export function ColorPicker({ label, value, onChange }: ColorPickerProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Convert named color to hex for display
  const namedColor = namedColors.find((c) => c.name === value);
  const displayColor = namedColor?.hex || (value.startsWith('#') ? value : '#' + value);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">{label}</label>

      {/* Named color quick picks */}
      <div className="flex flex-wrap gap-2">
        {namedColors.map((color) => (
          <button
            key={color.name}
            onClick={() => onChange(color.name)}
            className={`
              w-8 h-8 rounded border-2 transition-all
              ${
                value === color.name || value === color.hex
                  ? 'border-blue-500 scale-110'
                  : 'border-gray-300 hover:border-gray-400'
              }
            `}
            style={{ backgroundColor: color.hex }}
            title={color.name}
          />
        ))}
      </div>

      {/* Hex color picker */}
      <Popover.Root open={isOpen} onOpenChange={setIsOpen}>
        <Popover.Trigger asChild>
          <button
            className="w-full h-10 rounded border border-gray-300 flex items-center justify-between px-3 hover:border-gray-400"
            style={{ backgroundColor: displayColor }}
          >
            <span
              className="text-sm font-mono"
              style={{
                color: displayColor === '#FFFFFF' || displayColor === '#FFFF00' ? '#000' : '#FFF',
              }}
            >
              {value}
            </span>
          </button>
        </Popover.Trigger>
        <Popover.Portal>
          <Popover.Content
            className="bg-white p-3 rounded-lg shadow-lg border border-gray-200"
            sideOffset={5}
          >
            <HexColorPicker
              color={displayColor}
              onChange={(hex) => onChange(hex)}
            />
            <Popover.Arrow className="fill-white" />
          </Popover.Content>
        </Popover.Portal>
      </Popover.Root>
    </div>
  );
}

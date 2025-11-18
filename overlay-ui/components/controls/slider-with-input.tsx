'use client';

import { useState, useEffect } from 'react';

interface SliderWithInputProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (value: number) => void;
  formatDisplay?: (value: number) => string;
}

export function SliderWithInput({
  label,
  value,
  min,
  max,
  step = 1,
  unit = '',
  onChange,
  formatDisplay,
}: SliderWithInputProps) {
  const [inputValue, setInputValue] = useState(value.toString());

  // Sync input value when prop changes
  useEffect(() => {
    setInputValue(value.toString());
  }, [value]);

  const displayValue = formatDisplay ? formatDisplay(value) : `${value}${unit}`;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    const numValue = parseFloat(newValue);
    if (!isNaN(numValue) && numValue >= min && numValue <= max) {
      onChange(numValue);
    }
  };

  const handleInputBlur = () => {
    // Clamp to min/max if out of range
    const numValue = parseFloat(inputValue);
    if (isNaN(numValue) || numValue < min) {
      onChange(min);
      setInputValue(min.toString());
    } else if (numValue > max) {
      onChange(max);
      setInputValue(max.toString());
    } else {
      // Round to step
      const rounded = Math.round(numValue / step) * step;
      onChange(rounded);
      setInputValue(rounded.toString());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleInputBlur();
      e.currentTarget.blur();
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center gap-2">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500 min-w-[60px] text-right">{displayValue}</span>
          <input
            type="number"
            min={min}
            max={max}
            step={step}
            value={inputValue}
            onChange={handleInputChange}
            onBlur={handleInputBlur}
            onKeyDown={handleKeyDown}
            className="w-20 px-2 py-1 text-sm text-right border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => {
          const newValue = Number(e.target.value);
          onChange(newValue);
          setInputValue(newValue.toString());
        }}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
      />
    </div>
  );
}

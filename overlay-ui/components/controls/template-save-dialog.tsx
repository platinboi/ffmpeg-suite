'use client';

import { useState } from 'react';
import { useEditorStore } from '@/lib/store';
import { OverlayAPI } from '@/lib/api';
import { X } from 'lucide-react';

interface TemplateSaveDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved: () => void;
}

export function TemplateSaveDialog({ isOpen, onClose, onSaved }: TemplateSaveDialogProps) {
  const settings = useEditorStore((state) => state.settings);
  const [templateName, setTemplateName] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!templateName.trim()) {
      setError('Template name is required');
      return;
    }

    // Validate template name
    if (!/^[a-zA-Z0-9_-]+$/.test(templateName)) {
      setError('Template name can only contain letters, numbers, hyphens, and underscores');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await OverlayAPI.createTemplate({
        name: templateName,
        font_size: settings.font_size || 54,
        font_weight: settings.font_weight || 500,
        text_color: settings.text_color || '#FFFFFF',
        border_width: settings.border_width || 0,
        border_color: settings.border_color || '#000000',
        shadow_x: settings.shadow_x || 0,
        shadow_y: settings.shadow_y || 0,
        shadow_color: settings.shadow_color || '#000000',
        position: settings.position || 'center',
        background_enabled: settings.background_enabled || false,
        background_color: settings.background_color || '#000000',
        background_opacity: settings.background_opacity || 0.0,
        text_opacity: settings.text_opacity || 1.0,
        alignment: settings.alignment || 'center',
        max_text_width_percent: settings.max_text_width_percent || 80,
      });

      setTemplateName('');
      onSaved();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save template');
      console.error('Failed to save template:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    setTemplateName('');
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Save as Template</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Template Name
            </label>
            <input
              type="text"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              placeholder="e.g., TikTok-Bold"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
            <p className="mt-1 text-xs text-gray-500">
              Only letters, numbers, hyphens, and underscores
            </p>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div className="bg-gray-50 p-3 rounded-md">
            <p className="text-xs font-medium text-gray-700 mb-2">Current Settings:</p>
            <div className="text-xs text-gray-600 space-y-1">
              <p>Font: {settings.font_size}px, weight {settings.font_weight}</p>
              <p>Colors: {settings.text_color} / {settings.border_color}</p>
              <p>Position: {settings.position}</p>
              <p>Text Width: {settings.max_text_width_percent}%</p>
            </div>
          </div>
        </div>

        <div className="flex gap-2 p-4 border-t border-gray-200">
          <button
            onClick={handleClose}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            disabled={saving}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !templateName.trim()}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Template'}
          </button>
        </div>
      </div>
    </div>
  );
}

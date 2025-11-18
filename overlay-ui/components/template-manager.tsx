'use client';

import { useState } from 'react';
import { Save, Trash2, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { TemplateSelector } from './controls/template-selector';
import { TemplateSaveDialog } from './controls/template-save-dialog';
import { useEditorStore } from '@/lib/store';
import { OverlayAPI } from '@/lib/api';

export function TemplateManager() {
  const selectedTemplate = useEditorStore((state) => state.selectedTemplate);
  const [isExpanded, setIsExpanded] = useState(true);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleDelete = async () => {
    if (!selectedTemplate) return;

    if (selectedTemplate === 'default') {
      alert('Cannot delete the default template');
      return;
    }

    if (!confirm(`Are you sure you want to delete the template "${selectedTemplate}"?`)) {
      return;
    }

    try {
      setDeleting(true);
      await OverlayAPI.deleteTemplate(selectedTemplate);

      // Trigger re-fetch of templates
      setRefreshKey(prev => prev + 1);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete template');
      console.error('Failed to delete template:', err);
    } finally {
      setDeleting(false);
    }
  };

  const handleSaved = () => {
    // Trigger re-fetch of templates
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="border-b border-gray-200 pb-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 rounded-lg transition-colors"
      >
        <div className="flex items-center gap-2 text-gray-700 font-medium">
          <FileText className="w-4 h-4" />
          <span>Templates</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 space-y-3">
          <div key={refreshKey}>
            <TemplateSelector />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setShowSaveDialog(true)}
              className="flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>Save as Template</span>
            </button>

            <button
              onClick={handleDelete}
              disabled={!selectedTemplate || selectedTemplate === 'default' || deleting}
              className="flex items-center justify-center gap-2 px-3 py-2 border border-red-300 text-red-700 text-sm rounded-md hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 className="w-4 h-4" />
              <span>{deleting ? 'Deleting...' : 'Delete'}</span>
            </button>
          </div>

          {selectedTemplate && selectedTemplate !== 'default' && (
            <div className="text-xs text-gray-500 italic">
              Modifying settings will not update the template. Save as new template to persist changes.
            </div>
          )}
        </div>
      )}

      <TemplateSaveDialog
        isOpen={showSaveDialog}
        onClose={() => setShowSaveDialog(false)}
        onSaved={handleSaved}
      />
    </div>
  );
}

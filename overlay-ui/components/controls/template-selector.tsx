'use client';

import { useEffect, useState } from 'react';
import { useEditorStore } from '@/lib/store';
import { OverlayAPI } from '@/lib/api';
import type { Template } from '@/lib/types';

export function TemplateSelector() {
  const selectedTemplate = useEditorStore((state) => state.selectedTemplate);
  const setSelectedTemplate = useEditorStore((state) => state.setSelectedTemplate);
  const loadTemplate = useEditorStore((state) => state.loadTemplate);

  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await OverlayAPI.getTemplates();

      // Convert templates object to array
      const templateArray = Object.entries(response.templates || {}).map(([name, data]: [string, any]) => ({
        name,
        ...data,
      })) as Template[];

      setTemplates(templateArray);

      // Set default template as selected if none selected
      if (!selectedTemplate && templateArray.length > 0) {
        const defaultTemplate = templateArray.find(t => t.is_default) || templateArray[0];
        setSelectedTemplate(defaultTemplate.name);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load templates');
      console.error('Failed to load templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTemplate = async (templateName: string) => {
    try {
      setSelectedTemplate(templateName);

      // Load full template details
      const template = await OverlayAPI.getTemplate(templateName);
      loadTemplate(template);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load template');
      console.error('Failed to load template:', err);
    }
  };

  if (loading) {
    return (
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Template</label>
        <div className="text-sm text-gray-500">Loading templates...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Template</label>
        <div className="text-sm text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700">Template</label>
      <select
        value={selectedTemplate || ''}
        onChange={(e) => handleSelectTemplate(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="" disabled>Select a template</option>
        {templates.map((template) => (
          <option key={template.name} value={template.name}>
            {template.name}
            {template.is_default && ' (Default)'}
          </option>
        ))}
      </select>

      {selectedTemplate && (
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
          <span>Using: {selectedTemplate}</span>
        </div>
      )}
    </div>
  );
}

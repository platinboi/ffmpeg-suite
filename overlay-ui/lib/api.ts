import type { FFmpegSettings, OverlayResponse, HealthResponse, Template } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class OverlayAPI {
  // Process a single file upload
  static async processFile(file: File, settings: FFmpegSettings): Promise<Blob> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('text', settings.text);
    formData.append('template', settings.template);
    formData.append('overrides', JSON.stringify(settings.overrides));

    if (settings.output_format) {
      formData.append('output_format', settings.output_format);
    }

    const response = await fetch(`/api/overlay/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Processing failed');
    }

    return await response.blob();
  }

  // Process from URL
  static async processUrl(url: string, settings: FFmpegSettings): Promise<Blob> {
    const response = await fetch(`/api/overlay/url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url,
        text: settings.text,
        template: settings.template,
        overrides: settings.overrides,
        output_format: settings.output_format,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Processing failed');
    }

    return await response.blob();
  }

  // Get available templates
  static async getTemplates(): Promise<any> {
    const response = await fetch(`/api/templates`);

    if (!response.ok) {
      throw new Error('Failed to fetch templates');
    }

    return await response.json();
  }

  // Get specific template
  static async getTemplate(name: string): Promise<Template> {
    const response = await fetch(`/api/templates/${name}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch template: ${name}`);
    }

    return await response.json();
  }

  // Create new template
  static async createTemplate(templateData: Omit<Template, 'font_path' | 'created_at' | 'updated_at' | 'is_default'>): Promise<Template> {
    const response = await fetch(`/api/templates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(templateData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create template');
    }

    return await response.json();
  }

  // Update template
  static async updateTemplate(name: string, templateData: Partial<Template>): Promise<Template> {
    const response = await fetch(`/api/templates/${name}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(templateData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update template');
    }

    return await response.json();
  }

  // Delete template
  static async deleteTemplate(name: string): Promise<void> {
    const response = await fetch(`/api/templates/${name}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete template');
    }
  }

  // Duplicate template
  static async duplicateTemplate(sourceName: string, newName: string): Promise<Template> {
    const response = await fetch(`/api/templates/${sourceName}/duplicate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ new_name: newName }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to duplicate template');
    }

    return await response.json();
  }

  // Health check
  static async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`/api/health`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return await response.json();
  }
}

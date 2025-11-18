import type { FFmpegSettings, OverlayResponse, HealthResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

    const response = await fetch(`${API_URL}/overlay/upload`, {
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
    const response = await fetch(`${API_URL}/overlay/url`, {
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
    const response = await fetch(`${API_URL}/templates`);

    if (!response.ok) {
      throw new Error('Failed to fetch templates');
    }

    return await response.json();
  }

  // Health check
  static async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_URL}/health`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return await response.json();
  }
}

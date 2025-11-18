// Text styling options matching backend schema
export interface TextOverrideOptions {
  font_family?: 'regular' | 'bold';
  font_size?: number;
  text_color?: string;
  border_width?: number;
  border_color?: string;
  shadow_x?: number;
  shadow_y?: number;
  shadow_color?: string;
  background_enabled?: boolean;
  background_color?: string;
  background_opacity?: number;
  text_opacity?: number;
  position?: 'center' | 'top-left' | 'top-right' | 'top-center' | 'bottom-left' | 'bottom-right' | 'bottom-center' | 'middle-left' | 'middle-right' | 'custom';
  custom_x?: number;
  custom_y?: number;
  alignment?: 'left' | 'center' | 'right';
}

// Template interface
export interface Template {
  id: string;
  name: string;
  description?: string;
  createdAt: Date;
  settings: TextOverrideOptions;
  text?: string;
  thumbnail?: string;
}

// Editor state
export interface EditorState {
  file: File | null;
  fileUrl: string | null;
  sourceUrl: string | null; // For URL-based uploads
  fileSource: 'upload' | 'url';
  imageDimensions: { width: number; height: number } | null;
  text: string;
  settings: TextOverrideOptions;
  position: { x: number; y: number };
  positionMode: 'preset' | 'custom';
}

// FFmpeg settings for API
export interface FFmpegSettings {
  text: string;
  template: string;
  overrides: TextOverrideOptions;
  output_format?: 'same' | 'mp4' | 'jpg' | 'png';
}

// API response types
export interface OverlayResponse {
  status: 'success' | 'error';
  message: string;
  filename?: string;
  download_url?: string;
  processing_time?: number;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  ffmpeg_available: boolean;
  fonts_available: boolean;
  version: string;
}

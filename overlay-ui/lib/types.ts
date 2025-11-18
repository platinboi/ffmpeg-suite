export interface TextOverrideOptions {
  font_size?: number;
  font_weight?: number; // 100-900 for fine-grained control
  text_color?: string;
  border_width?: number;
  border_color?: string;
  shadow_x?: number;
  shadow_y?: number;
  shadow_color?: string;
  position?: string;
  background_enabled?: boolean;
  background_color?: string;
  background_opacity?: number;
  text_opacity?: number;
  alignment?: 'left' | 'center' | 'right';
  max_text_width_percent?: number; // 10-100, percentage of image width for text wrapping
  font_family?: 'regular' | 'bold'; // Deprecated, use font_weight instead
}

export interface EditorState {
  file: File | null;
  fileUrl: string | null;
  sourceUrl: string | null;
  fileSource: 'upload' | 'url';
  imageDimensions: { width: number; height: number } | null;
  text: string;
  settings: TextOverrideOptions;
  position: { x: number; y: number };
  positionMode: 'preset' | 'custom';
}

export interface FFmpegSettings {
  text: string;
  template: string;
  overrides: TextOverrideOptions;
  output_format?: string;
}

export interface OverlayResponse {
  message: string;
  file_url?: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export interface Template {
  name: string;
  font_path?: string; // Backend only
  font_size: number;
  font_weight: number;
  text_color: string;
  border_width: number;
  border_color: string;
  shadow_x: number;
  shadow_y: number;
  shadow_color: string;
  position: string;
  background_enabled: boolean;
  background_color: string;
  background_opacity: number;
  text_opacity: number;
  alignment: 'left' | 'center' | 'right';
  max_text_width_percent: number;
  created_at?: string;
  updated_at?: string;
  is_default?: boolean;
}

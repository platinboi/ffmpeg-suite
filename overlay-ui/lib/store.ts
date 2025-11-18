import { create } from 'zustand';
import type { EditorState, TextOverrideOptions, Template } from './types';

interface EditorActions {
  setFile: (file: File) => void;
  setFileUrl: (url: string | null) => void;
  setSourceUrl: (url: string | null) => void;
  setFileSource: (source: 'upload' | 'url') => void;
  setImageDimensions: (dimensions: { width: number; height: number } | null) => void;
  setText: (text: string) => void;
  updateSetting: <K extends keyof TextOverrideOptions>(
    key: K,
    value: TextOverrideOptions[K]
  ) => void;
  setPosition: (x: number, y: number) => void;
  setPositionMode: (mode: 'preset' | 'custom') => void;
  selectedTemplate: string | null;
  setSelectedTemplate: (name: string | null) => void;
  loadTemplate: (template: Template) => void;
  reset: () => void;
}

const defaultSettings: TextOverrideOptions = {
  font_size: 54,
  font_weight: 500,
  text_color: '#FFFFFF',
  border_width: 3,
  border_color: '#000000',
  shadow_x: 0,
  shadow_y: 0,
  shadow_color: '#000000',
  position: 'center',
  background_enabled: false,
  background_color: '#000000',
  background_opacity: 0.0,
  text_opacity: 1.0,
  alignment: 'center',
  max_text_width_percent: 80,
};

const initialState: EditorState = {
  file: null,
  fileUrl: null,
  sourceUrl: null,
  fileSource: 'upload',
  imageDimensions: null,
  text: '',
  settings: { ...defaultSettings },
  position: { x: 0, y: 0 },
  positionMode: 'preset',
};

export const useEditorStore = create<EditorState & EditorActions>((set) => ({
  ...initialState,
  selectedTemplate: null,

  setFile: (file) => set({ file }),

  setFileUrl: (url) => set({ fileUrl: url }),

  setSourceUrl: (url) => set({ sourceUrl: url }),

  setFileSource: (source) => set({ fileSource: source }),

  setImageDimensions: (dimensions) => set({ imageDimensions: dimensions }),

  setText: (text) => set({ text }),

  updateSetting: (key, value) =>
    set((state) => ({
      settings: {
        ...state.settings,
        [key]: value,
      },
    })),

  setPosition: (x, y) =>
    set({
      position: { x, y },
      positionMode: 'custom',
    }),

  setPositionMode: (mode) => set({ positionMode: mode }),

  setSelectedTemplate: (name) => set({ selectedTemplate: name }),

  loadTemplate: (template: Template) =>
    set({
      settings: {
        font_size: template.font_size,
        font_weight: template.font_weight,
        text_color: template.text_color,
        border_width: template.border_width,
        border_color: template.border_color,
        shadow_x: template.shadow_x,
        shadow_y: template.shadow_y,
        shadow_color: template.shadow_color,
        position: template.position,
        background_enabled: template.background_enabled,
        background_color: template.background_color,
        background_opacity: template.background_opacity,
        text_opacity: template.text_opacity,
        alignment: template.alignment,
        max_text_width_percent: template.max_text_width_percent,
      },
      selectedTemplate: template.name,
    }),

  reset: () => set(initialState),
}));

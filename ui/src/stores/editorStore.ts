import { create } from 'zustand';
import type { EditorState, TextOverrideOptions } from '../types';

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
  reset: () => void;
}

const defaultSettings: TextOverrideOptions = {
  font_size: 54,
  text_color: 'white',
  border_width: 3,
  border_color: 'black',
  shadow_x: 0,
  shadow_y: 0,
  shadow_color: 'black',
  position: 'center',
  background_enabled: false,
  background_color: 'black',
  background_opacity: 0.0,
  text_opacity: 1.0,
  alignment: 'center',
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

  reset: () => set(initialState),
}));

import { useEffect, useRef } from 'react';
import type { TextOverrideOptions } from '../../types';
import { hexToRgba } from '../../lib/utils';

interface PreviewCanvasProps {
  imageUrl: string;
  text: string;
  settings: TextOverrideOptions;
  position: { x: number; y: number };
  onCanvasReady?: (canvas: HTMLCanvasElement) => void;
}

export function PreviewCanvas({
  imageUrl,
  text,
  settings,
  position,
  onCanvasReady,
}: PreviewCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.crossOrigin = 'anonymous';

    img.onload = () => {
      // Set canvas dimensions to match image
      canvas.width = img.width;
      canvas.height = img.height;

      // Draw base image
      ctx.drawImage(img, 0, 0);

      if (!text) {
        if (onCanvasReady) onCanvasReady(canvas);
        return;
      }

      // Calculate position
      const fontSize = settings.font_size || 54;
      let textX = 0;
      let textY = 0;

      // Use preset positions if in preset mode
      if (settings.position && settings.position !== 'custom') {
        const positions: Record<string, [number, number]> = {
          center: [img.width / 2, img.height / 2],
          'top-left': [50, fontSize],
          'top-right': [img.width - 50, fontSize],
          'top-center': [img.width / 2, fontSize],
          'bottom-left': [50, img.height - 50],
          'bottom-right': [img.width - 50, img.height - 50],
          'bottom-center': [img.width / 2, img.height - 50],
          'middle-left': [50, img.height / 2],
          'middle-right': [img.width - 50, img.height / 2],
        };

        if (positions[settings.position]) {
          [textX, textY] = positions[settings.position];
        }
      } else {
        // Custom position mode
        textX = position.x;
        textY = position.y;
      }

      // Apply offsets from the offset sliders
      textX += position.x;
      textY += position.y;

      // Set font
      const fontWeight = settings.font_family === 'bold' ? 'bold' : 'normal';
      ctx.font = `${fontWeight} ${fontSize}px Arial, sans-serif`;

      // Set text alignment
      const alignment = settings.alignment || 'center';
      ctx.textAlign = alignment;
      ctx.textBaseline = 'middle';

      // Draw background box if enabled
      if (settings.background_enabled) {
        const metrics = ctx.measureText(text);
        const padding = 10;
        let boxX = textX - padding;

        if (alignment === 'center') {
          boxX = textX - metrics.width / 2 - padding;
        } else if (alignment === 'right') {
          boxX = textX - metrics.width - padding;
        }

        const bgColor = hexToRgba(
          settings.background_color || 'black',
          settings.background_opacity || 0.5
        );

        ctx.fillStyle = bgColor;
        ctx.fillRect(
          boxX,
          textY - fontSize / 2 - padding,
          metrics.width + padding * 2,
          fontSize + padding * 2
        );
      }

      // Draw shadow if enabled
      if ((settings.shadow_x !== 0 || settings.shadow_y !== 0) && settings.shadow_color) {
        ctx.shadowColor = hexToRgba(settings.shadow_color, 0.7);
        ctx.shadowOffsetX = settings.shadow_x || 0;
        ctx.shadowOffsetY = settings.shadow_y || 0;
        ctx.shadowBlur = 4;
      }

      // Draw text border (stroke)
      if (settings.border_width && settings.border_width > 0) {
        ctx.strokeStyle = settings.border_color || 'black';
        ctx.lineWidth = settings.border_width * 2; // Double for better visibility
        ctx.lineJoin = 'round';
        ctx.strokeText(text, textX, textY);
      }

      // Reset shadow
      ctx.shadowColor = 'transparent';
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;
      ctx.shadowBlur = 0;

      // Draw main text (fill)
      const textColor = hexToRgba(
        settings.text_color || 'white',
        settings.text_opacity || 1.0
      );
      ctx.fillStyle = textColor;
      ctx.fillText(text, textX, textY);

      if (onCanvasReady) onCanvasReady(canvas);
    };

    img.onerror = () => {
      console.error('Failed to load image');
    };

    img.src = imageUrl;
  }, [imageUrl, text, settings, position, onCanvasReady]);

  return (
    <canvas
      ref={canvasRef}
      className="max-w-full max-h-[70vh] object-contain shadow-lg"
    />
  );
}

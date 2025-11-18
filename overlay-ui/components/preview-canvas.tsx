'use client';

import { useEffect, useRef } from 'react';
import type { TextOverrideOptions } from '@/lib/types';
import { hexToRgba } from '@/lib/utils';

interface PreviewCanvasProps {
  imageUrl: string;
  text: string;
  settings: TextOverrideOptions;
  position: { x: number; y: number };
  positionMode: 'preset' | 'custom';
  onCanvasReady?: (canvas: HTMLCanvasElement) => void;
}

export function PreviewCanvas({
  imageUrl,
  text,
  settings,
  position,
  positionMode,
  onCanvasReady,
}: PreviewCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    // Don't set crossOrigin for blob URLs (file uploads and proxied URLs)
    // Only needed for external URLs, which we don't use anymore

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

      // FIXED: Use preset positions if in preset mode, otherwise use custom position
      if (positionMode === 'preset' && settings.position && settings.position !== 'custom') {
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
          // Apply offsets to preset position
          textX += position.x;
          textY += position.y;
        }
      } else {
        // Custom position mode - use position directly without adding twice
        textX = img.width / 2 + position.x;
        textY = img.height / 2 + position.y;
      }

      // Set font with numeric weight
      const fontWeight = settings.font_weight || 500;
      ctx.font = `${fontWeight} ${fontSize}px Arial, sans-serif`;

      // Set text alignment
      const alignment = settings.alignment || 'center';
      ctx.textAlign = alignment;
      ctx.textBaseline = 'middle';

      // Calculate max text width based on percentage of image width
      const maxTextWidthPercent = settings.max_text_width_percent || 80;
      const maxTextWidth = (img.width * maxTextWidthPercent) / 100;

      // Helper function to wrap text based on max width
      const wrapText = (text: string, maxWidth: number): string[] => {
        const allLines: string[] = [];
        // First split by manual line breaks (Enter key)
        const paragraphs = text.split('\n');

        paragraphs.forEach(paragraph => {
          if (!paragraph.trim()) {
            // Empty line - preserve it
            allLines.push('');
            return;
          }

          const words = paragraph.split(' ');
          let currentLine = '';

          words.forEach((word, index) => {
            const testLine = currentLine + (currentLine ? ' ' : '') + word;
            const metrics = ctx.measureText(testLine);

            if (metrics.width > maxWidth && currentLine !== '') {
              // Line is too long, push current line and start new one
              allLines.push(currentLine);
              currentLine = word;
            } else {
              currentLine = testLine;
            }

            // Push last word of paragraph
            if (index === words.length - 1 && currentLine) {
              allLines.push(currentLine);
            }
          });
        });

        return allLines;
      };

      // Wrap text into lines (respects manual breaks and auto-wraps long lines)
      const lines = wrapText(text, maxTextWidth);
      const lineHeight = fontSize * 1.2; // 20% line spacing
      const totalTextHeight = lineHeight * lines.length;

      // Calculate starting Y position (center the multi-line text block)
      const startY = textY - (totalTextHeight / 2) + (lineHeight / 2);

      // Measure all lines to find max width (for background box)
      let maxLineWidth = 0;
      lines.forEach(line => {
        const metrics = ctx.measureText(line);
        if (metrics.width > maxLineWidth) {
          maxLineWidth = metrics.width;
        }
      });

      // Draw background box if enabled
      if (settings.background_enabled) {
        const padding = 10;
        let boxX = textX - padding;

        if (alignment === 'center') {
          boxX = textX - maxLineWidth / 2 - padding;
        } else if (alignment === 'right') {
          boxX = textX - maxLineWidth - padding;
        }

        const bgColor = hexToRgba(
          settings.background_color || 'black',
          settings.background_opacity || 0.5
        );

        ctx.fillStyle = bgColor;
        ctx.fillRect(
          boxX,
          startY - lineHeight / 2 - padding,
          maxLineWidth + padding * 2,
          totalTextHeight + padding * 2
        );
      }

      // Render each line
      lines.forEach((line, index) => {
        const lineY = startY + (index * lineHeight);

        // Calculate X position for this line based on alignment
        let lineX = textX;
        if (alignment === 'center') {
          lineX = textX; // Already set textAlign to center
        } else if (alignment === 'left') {
          lineX = textX; // Already set textAlign to left
        } else if (alignment === 'right') {
          lineX = textX; // Already set textAlign to right
        }

        // Draw shadow for this line
        if ((settings.shadow_x !== 0 || settings.shadow_y !== 0) && settings.shadow_color) {
          ctx.shadowColor = hexToRgba(settings.shadow_color, 0.7);
          ctx.shadowOffsetX = settings.shadow_x || 0;
          ctx.shadowOffsetY = settings.shadow_y || 0;
          ctx.shadowBlur = 4;
        }

        // Draw text border (stroke) for this line
        if (settings.border_width && settings.border_width > 0) {
          ctx.strokeStyle = settings.border_color || 'black';
          ctx.lineWidth = settings.border_width * 2; // Double for better visibility
          ctx.lineJoin = 'round';
          ctx.strokeText(line, lineX, lineY);
        }

        // Reset shadow
        ctx.shadowColor = 'transparent';
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        ctx.shadowBlur = 0;

        // Draw main text (fill) for this line
        const textColor = hexToRgba(
          settings.text_color || 'white',
          settings.text_opacity || 1.0
        );
        ctx.fillStyle = textColor;
        ctx.fillText(line, lineX, lineY);
      });

      if (onCanvasReady) onCanvasReady(canvas);
    };

    img.onerror = (e) => {
      console.error('Failed to load image:', imageUrl, e);
    };

    img.src = imageUrl;
  }, [imageUrl, text, settings, position, positionMode, onCanvasReady]);

  return (
    <canvas
      ref={canvasRef}
      className="max-w-full max-h-[70vh] object-contain shadow-lg"
    />
  );
}

"""
FFmpeg service for adding text overlays to images and videos
"""
import subprocess
import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from config import Config, TextStyle, get_template
from models.schemas import TextOverrideOptions

logger = logging.getLogger(__name__)


class FFmpegService:
    """Handles FFmpeg text overlay operations"""

    @staticmethod
    def check_ffmpeg_available() -> bool:
        """Check if FFmpeg is installed and available"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @staticmethod
    def check_font_available(font_path: str) -> bool:
        """Check if font file exists"""
        return os.path.exists(font_path)

    @staticmethod
    def add_text_overlay(
        input_path: str,
        output_path: str,
        text: str,
        template_name: str = "default",
        overrides: Optional[TextOverrideOptions] = None
    ) -> Dict[str, Any]:
        """
        Add text overlay to video or image

        Args:
            input_path: Path to input file
            output_path: Path to output file
            text: Text to overlay
            template_name: Name of style template to use
            overrides: Optional style overrides

        Returns:
            Dict with status and details
        """
        try:
            # Get base template
            style = get_template(template_name)

            # Apply overrides if provided
            if overrides:
                style = FFmpegService._apply_overrides(style, overrides)

            # Get media dimensions for text wrapping
            media_info = FFmpegService.get_media_info(input_path)
            img_width = FFmpegService._get_video_width(media_info)

            # Wrap text if max_text_width_percent is specified
            if overrides and overrides.max_text_width_percent and img_width:
                text = FFmpegService._wrap_text(
                    text,
                    style.font_size,
                    img_width,
                    overrides.max_text_width_percent
                )

            # Build FFmpeg filter
            filter_str = FFmpegService._build_drawtext_filter(text, style, overrides)

            # Determine if input is image or video
            is_image = FFmpegService._is_image(input_path)

            # Build FFmpeg command
            cmd = FFmpegService._build_ffmpeg_command(
                input_path, output_path, filter_str, is_image
            )

            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")

            # Execute FFmpeg
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {process.stderr}")
                raise Exception(f"FFmpeg processing failed: {process.stderr}")

            # Verify output file was created
            if not os.path.exists(output_path):
                raise Exception("Output file was not created")

            output_size = os.path.getsize(output_path)
            logger.info(f"Successfully created output file: {output_path} ({output_size} bytes)")

            return {
                "success": True,
                "status": "success",
                "output_path": output_path,
                "output_size": output_size
            }

        except subprocess.TimeoutExpired:
            raise Exception("FFmpeg processing timed out (max 2 minutes)")
        except Exception as e:
            logger.error(f"Error adding text overlay: {str(e)}")
            raise

    @staticmethod
    def _apply_overrides(style: TextStyle, overrides: TextOverrideOptions) -> TextStyle:
        """Apply override options to base style"""
        # Create a copy of the style
        override_dict = overrides.model_dump(exclude_none=True)

        # Handle font weight override (preferred method)
        if 'font_weight' in override_dict:
            font_weight = override_dict.pop('font_weight')
            # Map numeric weight to available TikTok Sans fonts
            # 100-449 → Medium (500), 450-900 → SemiBold (600)
            if font_weight < 450:
                style.font_path = Config.TIKTOK_SANS_MEDIUM
            else:
                style.font_path = Config.TIKTOK_SANS_SEMIBOLD
        # Handle legacy font_family override (deprecated)
        elif 'font_family' in override_dict:
            font_family = override_dict.pop('font_family')
            if font_family == 'bold':
                style.font_path = Config.INTER_BOLD
            else:
                style.font_path = Config.INTER_REGULAR

        # Apply other overrides
        for key, value in override_dict.items():
            if hasattr(style, key):
                setattr(style, key, value)

        return style

    @staticmethod
    def _build_drawtext_filter(
        text: str,
        style: TextStyle,
        overrides: Optional[TextOverrideOptions] = None
    ) -> str:
        """Build FFmpeg drawtext filter string"""
        # Escape special characters for FFmpeg
        escaped_text = FFmpegService._escape_text(text)

        # Calculate position
        x, y = FFmpegService._calculate_position(style, overrides)

        # Convert colors to hex format
        text_color = FFmpegService._convert_color(style.text_color)
        border_color = FFmpegService._convert_color(style.border_color)
        shadow_color = FFmpegService._convert_color(style.shadow_color)
        bg_color = FFmpegService._convert_color(style.background_color)

        # Build filter parameters
        filter_params = [
            f"fontfile={style.font_path}",
            f"text='{escaped_text}'",
            f"fontsize={style.font_size}",
            f"fontcolor={text_color}@{style.text_opacity}",
            f"x={x}",
            f"y={y}",
        ]

        # Add border if enabled
        if style.border_width > 0:
            filter_params.append(f"borderw={style.border_width}")
            filter_params.append(f"bordercolor={border_color}")

        # Add shadow
        if style.shadow_x != 0 or style.shadow_y != 0:
            filter_params.append(f"shadowx={style.shadow_x}")
            filter_params.append(f"shadowy={style.shadow_y}")
            filter_params.append(f"shadowcolor={shadow_color}@0.7")

        # Add background box if enabled
        if style.background_enabled:
            filter_params.append("box=1")
            filter_params.append(f"boxcolor={bg_color}@{style.background_opacity}")
            filter_params.append("boxborderw=5")

        # Add alignment if specified
        if overrides and overrides.alignment:
            alignment_map = {"left": "left", "center": "center", "right": "right"}
            filter_params.append(f"text_align={alignment_map[overrides.alignment]}")

        return "drawtext=" + ":".join(filter_params)

    @staticmethod
    def _calculate_position(
        style: TextStyle,
        overrides: Optional[TextOverrideOptions] = None
    ) -> Tuple[str, str]:
        """Calculate x, y position for text"""
        position = style.position
        if overrides and overrides.position:
            position = overrides.position

        # Position presets
        positions = {
            "center": ("(w-text_w)/2", "(h-text_h)/2"),
            "top-left": ("10", "10"),
            "top-right": ("w-text_w-10", "10"),
            "top-center": ("(w-text_w)/2", "10"),
            "bottom-left": ("10", "h-text_h-10"),
            "bottom-right": ("w-text_w-10", "h-text_h-10"),
            "bottom-center": ("(w-text_w)/2", "h-text_h-10"),
            "middle-left": ("10", "(h-text_h)/2"),
            "middle-right": ("w-text_w-10", "(h-text_h)/2"),
        }

        if position == "custom" and overrides:
            if overrides.custom_x is not None and overrides.custom_y is not None:
                return (str(overrides.custom_x), str(overrides.custom_y))

        return positions.get(position, positions["center"])

    @staticmethod
    def _escape_text(text: str) -> str:
        """Escape special characters for FFmpeg drawtext filter"""
        # FFmpeg drawtext requires escaping certain characters
        # Escape backslashes first (must be first!)
        text = text.replace("\\", "\\\\")
        # Escape single quotes
        text = text.replace("'", "\\'")
        # Escape colons
        text = text.replace(":", "\\:")
        # Convert newlines to FFmpeg format for multi-line support
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "")  # Remove carriage returns
        return text

    @staticmethod
    def _convert_color(color: str) -> str:
        """Convert color name or hex to FFmpeg format"""
        color_map = {
            'white': '0xFFFFFF',
            'black': '0x000000',
            'red': '0xFF0000',
            'green': '0x00FF00',
            'blue': '0x0000FF',
            'yellow': '0xFFFF00',
            'cyan': '0x00FFFF',
            'magenta': '0xFF00FF',
            'orange': '0xFFA500',
            'purple': '0x800080',
            'pink': '0xFFC0CB',
            'gray': '0x808080',
            'grey': '0x808080'
        }

        color_lower = color.lower()
        if color_lower in color_map:
            return color_map[color_lower]

        # Handle hex colors
        if color.startswith('#'):
            return '0x' + color[1:]

        # Default to white if unknown
        return '0xFFFFFF'

    @staticmethod
    def _is_image(file_path: str) -> bool:
        """Check if file is an image based on extension"""
        image_extensions = {'.jpg', '.jpeg', '.png'}
        ext = Path(file_path).suffix.lower()
        return ext in image_extensions

    @staticmethod
    def _build_ffmpeg_command(
        input_path: str,
        output_path: str,
        filter_str: str,
        is_image: bool
    ) -> list:
        """Build complete FFmpeg command"""
        cmd = ['ffmpeg', '-y', '-i', input_path]

        if is_image:
            # For images, use simple filter
            cmd.extend([
                '-vf', filter_str,
                '-q:v', '2',  # High quality
                output_path
            ])
        else:
            # For videos, preserve audio and use appropriate codecs
            cmd.extend([
                '-vf', filter_str,
                '-c:v', 'libx264',  # H.264 video codec
                '-preset', 'medium',  # Encoding speed/quality tradeoff
                '-crf', '23',  # Constant Rate Factor (quality)
                '-c:a', 'aac',  # AAC audio codec
                '-b:a', '128k',  # Audio bitrate
                '-movflags', '+faststart',  # Enable streaming
                output_path
            ])

        return cmd

    @staticmethod
    def get_media_info(file_path: str) -> Dict[str, Any]:
        """Get basic media information using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                return {}

        except Exception as e:
            logger.warning(f"Failed to get media info: {str(e)}")
            return {}

    @staticmethod
    def _get_video_width(media_info: Dict[str, Any]) -> Optional[int]:
        """Extract video/image width from media info"""
        try:
            if 'streams' in media_info:
                for stream in media_info['streams']:
                    if stream.get('codec_type') == 'video' and 'width' in stream:
                        return int(stream['width'])
            return None
        except Exception as e:
            logger.warning(f"Failed to extract video width: {str(e)}")
            return None

    @staticmethod
    def _wrap_text(
        text: str,
        font_size: int,
        img_width: int,
        max_width_percent: int
    ) -> str:
        """
        Wrap text based on max width percentage of image.
        Uses character-based approximation since we don't have exact font metrics.

        Args:
            text: Input text
            font_size: Font size in pixels
            img_width: Image width in pixels
            max_width_percent: Max text width as percentage (10-100)

        Returns:
            Text with newlines inserted for wrapping
        """
        max_width_px = (img_width * max_width_percent) / 100

        # Approximate character width (roughly 0.6 * font_size for most fonts)
        avg_char_width = font_size * 0.6
        max_chars_per_line = int(max_width_px / avg_char_width)

        # Ensure at least some characters per line
        if max_chars_per_line < 5:
            max_chars_per_line = 5

        wrapped_lines = []
        # Split by existing line breaks first
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            if not paragraph.strip():
                # Preserve empty lines
                wrapped_lines.append('')
                continue

            words = paragraph.split(' ')
            current_line = ''

            for word in words:
                test_line = current_line + (' ' if current_line else '') + word

                # Check if adding this word exceeds max chars
                if len(test_line) > max_chars_per_line and current_line:
                    wrapped_lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line

            # Add remaining text
            if current_line:
                wrapped_lines.append(current_line)

        return '\n'.join(wrapped_lines)

    @staticmethod
    def merge_videos(
        input_paths: List[str],
        output_path: str
    ) -> Dict[str, Any]:
        """
        Merge multiple video files into a single video using FFmpeg concat filter

        Args:
            input_paths: List of paths to video files to merge
            output_path: Path for the merged output file

        Returns:
            Dict with success status and metadata

        Raises:
            Exception: If merge fails or input validation fails
        """
        try:
            if len(input_paths) < 2:
                raise ValueError("At least 2 videos are required for merging")

            # Verify all input files exist
            for path in input_paths:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Input file not found: {path}")

            logger.info(f"Merging {len(input_paths)} videos into {output_path}")

            # Detect which inputs have audio streams
            has_audio = []
            for input_path in input_paths:
                media_info = FFmpegService.get_media_info(input_path)
                audio_stream_exists = False
                if 'streams' in media_info:
                    for stream in media_info['streams']:
                        if stream.get('codec_type') == 'audio':
                            audio_stream_exists = True
                            break
                has_audio.append(audio_stream_exists)

            logger.info(f"Audio stream detection: {has_audio}")

            # Determine audio handling strategy
            all_have_audio = all(has_audio)
            none_have_audio = not any(has_audio)

            if none_have_audio:
                # No audio in any clip - simple video-only concat
                inputs = []
                for i in range(len(input_paths)):
                    inputs.append(f"[{i}:v]")
                concat_filter = "".join(inputs) + f"concat=n={len(input_paths)}:v=1:a=0[v]"
                map_args = ['-map', '[v]']
                logger.info("Using video-only concat (no audio streams)")

            elif all_have_audio:
                # All clips have audio - standard concat
                inputs = []
                for i in range(len(input_paths)):
                    inputs.append(f"[{i}:v][{i}:a]")
                concat_filter = "".join(inputs) + f"concat=n={len(input_paths)}:v=1:a=1[v][a]"
                map_args = ['-map', '[v]', '-map', '[a]']
                logger.info("Using standard concat (all clips have audio)")

            else:
                # Mixed audio - add silent audio to clips without audio
                filter_parts = []
                inputs_with_audio = []

                for i, input_path in enumerate(input_paths):
                    if has_audio[i]:
                        # Clip has audio - use as-is
                        inputs_with_audio.append(f"[{i}:v][{i}:a]")
                    else:
                        # Clip has no audio - generate silent audio
                        filter_parts.append(
                            f"anullsrc=channel_layout=stereo:sample_rate=44100[silent{i}]"
                        )
                        inputs_with_audio.append(f"[{i}:v][silent{i}]")

                # Combine filters and concat
                if filter_parts:
                    filter_str = ";".join(filter_parts) + ";"
                else:
                    filter_str = ""
                concat_input = "".join(inputs_with_audio)
                concat_filter = f"{filter_str}{concat_input}concat=n={len(input_paths)}:v=1:a=1[v][a]"
                map_args = ['-map', '[v]', '-map', '[a]']
                logger.info("Using mixed concat (adding silent audio to clips without audio)")

            # Build FFmpeg command
            cmd = ['ffmpeg', '-y']

            # Add all input files
            for input_path in input_paths:
                cmd.extend(['-i', input_path])

            # Add filter_complex and output settings
            cmd.extend([
                '-filter_complex', concat_filter,
                *map_args,  # Unpack map arguments (varies based on audio strategy)
                '-c:v', 'libx264',  # H.264 video codec
                '-preset', 'medium',  # Encoding speed/quality tradeoff
                '-crf', '23',  # Constant Rate Factor (quality)
            ])

            # Only add audio codec settings if we have audio
            if not none_have_audio:
                cmd.extend([
                    '-c:a', 'aac',  # AAC audio codec
                    '-b:a', '128k',  # Audio bitrate
                ])

            cmd.extend([
                '-movflags', '+faststart',  # Enable streaming
                output_path
            ])

            logger.info(f"Running FFmpeg merge command: {' '.join(cmd)}")

            # Execute FFmpeg
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=Config.MERGE_TIMEOUT  # Configurable timeout for merging
            )

            if process.returncode != 0:
                logger.error(f"FFmpeg merge error: {process.stderr}")
                raise Exception(f"FFmpeg merge failed: {process.stderr}")

            # Verify output file was created
            if not os.path.exists(output_path):
                raise Exception("Merged output file was not created")

            output_size = os.path.getsize(output_path)

            # Get output video duration
            media_info = FFmpegService.get_media_info(output_path)
            duration = None
            if 'format' in media_info and 'duration' in media_info['format']:
                duration = float(media_info['format']['duration'])

            logger.info(f"Successfully merged {len(input_paths)} videos: {output_path} ({output_size} bytes, {duration}s)")

            return {
                "success": True,
                "output_path": output_path,
                "output_size": output_size,
                "duration": duration,
                "clips_merged": len(input_paths)
            }

        except subprocess.TimeoutExpired:
            timeout_mins = Config.MERGE_TIMEOUT / 60
            raise Exception(f"FFmpeg merge timed out (max {timeout_mins:.0f} minutes)")
        except Exception as e:
            logger.error(f"Error merging videos: {str(e)}")
            raise

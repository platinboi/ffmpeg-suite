"""
FFmpeg service for adding text overlays to images and videos
"""
import subprocess
import os
import tempfile
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from config import Config, TextStyle, get_template
from models.schemas import TextOverrideOptions

logger = logging.getLogger(__name__)

# Base resolution for font size scaling (1080p width)
# Font sizes in templates are designed for 1080p and will be scaled proportionally
BASE_RESOLUTION_WIDTH = 1080


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
        overrides: Optional[TextOverrideOptions] = None,
        apply_fade_out: bool = False,
        fade_out_duration: float = 2.5
    ) -> Dict[str, Any]:
        """
        Add text overlay to video or image

        Args:
            input_path: Path to input file
            output_path: Path to output file
            text: Text to overlay
            template_name: Name of style template to use
            overrides: Optional style overrides
            apply_fade_out: Whether to hide text in the final seconds
            fade_out_duration: Seconds before end to hide text (default 2.5)

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
            logger.info(f"[TEXT WRAP DEBUG] img_width from media: {img_width}")

            # Calculate scaled font size based on video resolution
            # This ensures consistent visual appearance across different resolutions
            if img_width:
                scale_factor = img_width / BASE_RESOLUTION_WIDTH
                scaled_font_size = int(style.font_size * scale_factor)
                logger.info(f"[FONT SCALING] Original font_size={style.font_size}, video_width={img_width}, scale_factor={scale_factor:.3f}, scaled_font_size={scaled_font_size}")
            else:
                # Fallback to original font size if width cannot be determined
                scaled_font_size = style.font_size
                logger.warning(f"[FONT SCALING] Could not determine video width, using original font_size={style.font_size}")

            # Wrap text if max_text_width_percent is specified (override or template default)
            max_text_width = overrides.max_text_width_percent if (overrides and overrides.max_text_width_percent) else style.max_text_width_percent
            logger.info(f"[TEXT WRAP DEBUG] max_text_width_percent: override={overrides.max_text_width_percent if overrides else None}, style={style.max_text_width_percent}, final={max_text_width}")

            if max_text_width and img_width:
                logger.info(f"[TEXT WRAP DEBUG] Condition passed! Wrapping text to {max_text_width}% of {img_width}px")
                text = FFmpegService._wrap_text(
                    text,
                    scaled_font_size,
                    style.font_path,
                    img_width,
                    max_text_width
                )
                logger.info(f"[TEXT WRAP DEBUG] Wrapped text result:\n{text}")
            else:
                logger.warning(f"[TEXT WRAP DEBUG] Condition FAILED! max_text_width={max_text_width}, img_width={img_width} - text wrapping SKIPPED")

            # Extract video duration if text hiding is requested
            video_duration = None
            if apply_fade_out:
                if 'format' in media_info and 'duration' in media_info['format']:
                    try:
                        video_duration = float(media_info['format']['duration'])
                        logger.info(f"Extracted video duration for text hiding: {video_duration}s")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to parse video duration for text hiding: {e}")
                        apply_fade_out = False
                else:
                    logger.warning("Video duration not available, skipping text hiding")
                    apply_fade_out = False

            # Build FFmpeg filter (returns tuple: filter_str, temp_file_path)
            filter_str, temp_file_path = FFmpegService._build_drawtext_filter(
                text,
                style,
                overrides,
                scaled_font_size=scaled_font_size,
                fade_out_duration=fade_out_duration if apply_fade_out else None,
                video_duration=video_duration if apply_fade_out else None
            )

            # Determine if input is image or video
            is_image = FFmpegService._is_image(input_path)

            # Build FFmpeg command
            cmd = FFmpegService._build_ffmpeg_command(
                input_path, output_path, filter_str, is_image
            )

            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")

            try:
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

            finally:
                # Clean up temporary text file
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                        logger.debug(f"Cleaned up temp text file: {temp_file_path}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to clean up temp file {temp_file_path}: {cleanup_error}")

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
        overrides: Optional[TextOverrideOptions] = None,
        scaled_font_size: Optional[int] = None,
        fade_out_duration: Optional[float] = None,
        video_duration: Optional[float] = None
    ) -> Tuple[str, str]:
        """
        Build FFmpeg drawtext filter string

        Args:
            text: Text to display
            style: Text style configuration
            overrides: Optional style overrides
            scaled_font_size: Font size scaled for video resolution (if None, uses style.font_size)
            fade_out_duration: Seconds before end to hide text (e.g., 2.5)
            video_duration: Total video duration in seconds (required if fade_out_duration is set)

        Returns:
            Tuple of (filter_string, temp_file_path)
        """
        # Write text to temporary file (avoids all FFmpeg escaping issues)
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False,
            encoding='utf-8'
        )
        temp_file.write(text)
        temp_file.close()
        temp_file_path = temp_file.name

        logger.debug(f"Created temp text file: {temp_file_path}")

        # Calculate position
        x, y = FFmpegService._calculate_position(style, overrides)

        # Convert colors to hex format
        text_color = FFmpegService._convert_color(style.text_color)
        border_color = FFmpegService._convert_color(style.border_color)
        shadow_color = FFmpegService._convert_color(style.shadow_color)
        bg_color = FFmpegService._convert_color(style.background_color)

        # Use scaled font size if provided, otherwise use style font size
        font_size = scaled_font_size if scaled_font_size is not None else style.font_size

        # Build filter parameters using textfile (no escaping needed)
        filter_params = [
            f"fontfile={style.font_path}",
            f"textfile={temp_file_path}",  # Use textfile - bypasses all escaping issues
            f"fontsize={font_size}",
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

        # Add alignment - FFmpeg uses single-letter flags: L (left), C (center), R (right)
        # Always add for center position to ensure multiline text centers properly
        if overrides and overrides.alignment:
            alignment_map = {"left": "L", "center": "C", "right": "R"}
            filter_params.append(f"text_align={alignment_map[overrides.alignment]}")
        elif style.position == "center":
            # Default to centered alignment for center position
            filter_params.append("text_align=C")

        # Add line spacing (negative for tighter TikTok-style spacing)
        line_spacing = overrides.line_spacing if (overrides and overrides.line_spacing is not None) else style.line_spacing
        filter_params.append(f"line_spacing={line_spacing}")

        # Add instant disappearance effect if requested
        if fade_out_duration is not None and video_duration is not None:
            # Calculate cutoff time (when text should disappear)
            cutoff_time = video_duration - fade_out_duration

            # Alpha expression: Full opacity until cutoff_time, then instantly invisible
            # if(lt(t,CUTOFF_TIME),1,0)
            alpha_expr = f"if(lt(t\\,{cutoff_time})\\,1\\,0)"
            filter_params.append(f"alpha='{alpha_expr}'")
            logger.info(f"Text will disappear at {cutoff_time}s (last {fade_out_duration}s hidden)")

        filter_str = "drawtext=" + ":".join(filter_params)
        return (filter_str, temp_file_path)

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
                '-preset', 'slow',  # Encoding speed/quality tradeoff (slow = better quality)
                '-crf', '18',  # Constant Rate Factor (18 = high quality, lower = better)
                '-c:a', 'aac',  # AAC audio codec
                '-b:a', '192k',  # Audio bitrate (higher quality audio)
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

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                logger.error(f"ffprobe failed for {file_path}: {result.stderr}")
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
    def _get_video_height(media_info: Dict[str, Any]) -> Optional[int]:
        """Extract video/image height from media info"""
        try:
            if 'streams' in media_info:
                for stream in media_info['streams']:
                    if stream.get('codec_type') == 'video' and 'height' in stream:
                        return int(stream['height'])
            return None
        except Exception as e:
            logger.warning(f"Failed to extract video height: {str(e)}")
            return None

    @staticmethod
    def _wrap_text(
        text: str,
        font_size: int,
        font_path: str,
        img_width: int,
        max_width_percent: int
    ) -> str:
        """
        Wrap text based on max width percentage using character-based estimation.
        Simple and reliable approach that doesn't depend on Pillow font loading.

        Args:
            text: Input text
            font_size: Font size in pixels
            font_path: Absolute path to font file (not used, kept for compatibility)
            img_width: Image width in pixels
            max_width_percent: Max text width as percentage (10-100)

        Returns:
            Text with newlines inserted for wrapping
        """
        max_width_px = (img_width * max_width_percent) / 100

        # Estimate average character width for the font
        # For TikTok Sans and similar fonts at typical sizes, ~0.55 * font_size works well
        avg_char_width = font_size * 0.55
        max_chars_per_line = int(max_width_px / avg_char_width)

        # Ensure minimum line length
        if max_chars_per_line < 10:
            max_chars_per_line = 10

        logger.info(f"[TEXT WRAP] max_width_px={max_width_px}, avg_char_width={avg_char_width}, max_chars={max_chars_per_line}")

        wrapped_lines = []
        # Split by existing line breaks first (preserve manual newlines)
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            if not paragraph.strip():
                # Preserve empty lines
                wrapped_lines.append('')
                continue

            words = paragraph.split(' ')
            current_line = ''

            for word in words:
                # Test adding this word to the current line
                test_line = current_line + (' ' if current_line else '') + word

                # Check if adding this word exceeds max character count
                if len(test_line) > max_chars_per_line and current_line:
                    # Current line is full, start new line
                    wrapped_lines.append(current_line)
                    current_line = word
                else:
                    # Word fits, add to current line
                    current_line = test_line

            # Add remaining text
            if current_line:
                wrapped_lines.append(current_line)

        return '\n'.join(wrapped_lines)

    async def trim_video(
        self,
        input_path: str,
        output_path: str,
        target_duration: float,
        trim_mode: str = "both"
    ) -> Dict[str, Any]:
        """
        Trim a video to a target duration.

        Args:
            input_path: Path to input video
            output_path: Path to output trimmed video
            target_duration: Desired duration in seconds
            trim_mode: 'start' (cut from beginning), 'end' (cut from end), 'both' (split equally)

        Returns:
            Dict with success status and new duration
        """
        import asyncio

        # Get original duration (get_media_info is synchronous)
        media_info = self.get_media_info(input_path)
        original_duration = float(media_info['format']['duration'])

        # Validate: can't extend, only trim
        if target_duration >= original_duration:
            logger.info(f"Target duration {target_duration}s >= original {original_duration}s, skipping trim")
            return {"trimmed": False, "duration": original_duration}

        # Calculate trim amounts
        trim_total = original_duration - target_duration

        if trim_mode == "start":
            start_time = trim_total
            end_time = original_duration
        elif trim_mode == "end":
            start_time = 0
            end_time = target_duration
        else:  # "both"
            start_time = trim_total / 2
            end_time = original_duration - (trim_total / 2)

        # FFmpeg trim command with accurate seeking (-ss after -i)
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-ss', str(start_time),
            '-to', str(end_time),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '18',
            '-an',  # No audio (consistent with merge pipeline)
            output_path
        ]

        logger.info(f"Trimming video: {original_duration:.2f}s → {target_duration:.2f}s (mode={trim_mode}, start={start_time:.2f}s, end={end_time:.2f}s)")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg trim failed: {stderr.decode()}")

        logger.info(f"Successfully trimmed video to {target_duration}s")
        return {"trimmed": True, "duration": target_duration, "original_duration": original_duration}

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

            # Normalize fps and pixel format before concat to prevent timestamp issues
            # Different frame rates between clips cause corrupted playback
            normalize_filters = []
            normalized_inputs = []
            for i in range(len(input_paths)):
                normalize_filters.append(f"[{i}:v]fps=30,format=yuv420p[v{i}]")
                normalized_inputs.append(f"[v{i}]")

            concat_filter = ";".join(normalize_filters) + ";" + "".join(normalized_inputs) + f"concat=n={len(input_paths)}:v=1:a=0[v]"
            map_args = ['-map', '[v]']
            logger.info("Using video-only concat with fps/format normalization")

            # Build FFmpeg command
            cmd = ['ffmpeg', '-y']

            # Add all input files
            for input_path in input_paths:
                cmd.extend(['-i', input_path])

            # Add filter_complex and output settings
            cmd.extend([
                '-filter_complex', concat_filter,
                *map_args,
                '-c:v', 'libx264',  # H.264 video codec
                '-preset', 'slow',  # Encoding speed/quality tradeoff (slow = better quality)
                '-crf', '18',  # Constant Rate Factor (18 = high quality, lower = better)
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

    @staticmethod
    def scale_video(
        input_path: str,
        output_path: str,
        target_width: int,
        target_height: int
    ) -> Dict[str, Any]:
        """
        Scale a video to target resolution with aspect ratio preservation and padding

        Args:
            input_path: Path to input video
            output_path: Path to save scaled video
            target_width: Target width in pixels
            target_height: Target height in pixels

        Returns:
            Dictionary with success status and output info

        Raises:
            Exception: If scaling fails
        """
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")

            logger.info(f"Scaling video {input_path} to {target_width}x{target_height}")

            # Get current video dimensions
            media_info = FFmpegService.get_media_info(input_path)
            current_width = FFmpegService._get_video_width(media_info)
            current_height = FFmpegService._get_video_height(media_info)

            if current_width == target_width and current_height == target_height:
                # Already correct size - just copy
                logger.info(f"Video already at target resolution, copying: {input_path}")
                import shutil
                shutil.copy2(input_path, output_path)
                return {
                    "success": True,
                    "output_path": output_path,
                    "scaled": False
                }

            # Build FFmpeg command with scale + pad filters
            # This maintains aspect ratio and centers video with black bars
            filter_str = (
                f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
                f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2"
            )

            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-vf', filter_str,
                '-c:v', 'libx264',  # Re-encode video
                '-preset', 'medium',
                '-crf', '23',  # Quality setting
                '-c:a', 'copy',  # Copy audio without re-encoding
                '-movflags', '+faststart',
                output_path
            ]

            logger.info(f"Running FFmpeg scale command: {' '.join(cmd)}")

            # Execute FFmpeg
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if process.returncode != 0:
                logger.error(f"FFmpeg scale error: {process.stderr}")
                raise Exception(f"FFmpeg scale failed: {process.stderr}")

            # Verify output file was created
            if not os.path.exists(output_path):
                raise Exception("Scaled output file was not created")

            output_size = os.path.getsize(output_path)
            logger.info(f"Successfully scaled video: {output_path} ({output_size} bytes)")

            return {
                "success": True,
                "output_path": output_path,
                "output_size": output_size,
                "scaled": True
            }

        except subprocess.TimeoutExpired:
            raise Exception("FFmpeg scaling timed out (max 2 minutes)")
        except Exception as e:
            logger.error(f"Error scaling video: {str(e)}")
            raise

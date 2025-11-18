"""
Service for merging multiple video clips with text overlays
"""
import asyncio
import os
import uuid
import logging
from typing import List, Dict, Tuple
from config import Config
from services.download_service import DownloadService
from services.ffmpeg_service import FFmpegService
from models.schemas import TextOverrideOptions

logger = logging.getLogger(__name__)


class MergeService:
    """Handles downloading, processing, and merging multiple video clips"""

    def __init__(self):
        self.download_service = DownloadService()
        self.ffmpeg_service = FFmpegService()

    async def download_clips(self, clip_urls: List[str]) -> List[Tuple[str, str]]:
        """
        Download multiple clips in parallel

        Args:
            clip_urls: List of URLs to download

        Returns:
            List of tuples (file_path, content_type)

        Raises:
            Exception: If any download fails
        """
        logger.info(f"Downloading {len(clip_urls)} clips in parallel")

        # Download all clips concurrently
        download_tasks = [
            self.download_service.download_from_url(url)
            for url in clip_urls
        ]

        try:
            results = await asyncio.gather(*download_tasks)
            logger.info(f"Successfully downloaded {len(results)} clips")
            return results
        except Exception as e:
            logger.error(f"Failed to download clips: {str(e)}")
            raise Exception(f"Clip download failed: {str(e)}")

    def apply_overlays_to_clips(
        self,
        clip_configs: List[Dict],
        downloaded_clips: List[Tuple[str, str]]
    ) -> List[str]:
        """
        Apply text overlays to each downloaded clip

        Args:
            clip_configs: List of clip configurations with text/template/overrides
            downloaded_clips: List of tuples (file_path, content_type)

        Returns:
            List of paths to overlayed clip files

        Raises:
            Exception: If overlay processing fails
        """
        overlayed_paths = []

        try:
            for i, ((clip_path, content_type), config) in enumerate(zip(downloaded_clips, clip_configs)):
                logger.info(f"Applying overlay to clip {i+1}/{len(clip_configs)}: {config.get('text')}")

                # Generate output path for overlayed clip
                output_filename = f"overlayed_{uuid.uuid4()}.mp4"
                output_path = os.path.join(Config.TEMP_DIR, output_filename)

                # Parse overrides if provided
                overrides = None
                if config.get('overrides'):
                    try:
                        overrides = TextOverrideOptions(**config['overrides'])
                    except Exception as e:
                        logger.warning(f"Failed to parse overrides for clip {i+1}: {e}")

                # Apply text overlay using FFmpeg service
                result = self.ffmpeg_service.add_text_overlay(
                    input_path=clip_path,
                    output_path=output_path,
                    text=config['text'],
                    template_name=config.get('template', 'default'),
                    overrides=overrides
                )

                if not result.get('success'):
                    raise Exception(f"Failed to apply overlay to clip {i+1}")

                overlayed_paths.append(output_path)
                logger.info(f"Successfully overlayed clip {i+1}: {output_path}")

            return overlayed_paths

        except Exception as e:
            # Cleanup any partially processed files
            for path in overlayed_paths:
                self.cleanup_file(path)
            raise Exception(f"Overlay processing failed: {str(e)}")

    def merge_clips(self, overlayed_paths: List[str], output_path: str) -> Dict:
        """
        Merge multiple overlayed clips into a single video

        Args:
            overlayed_paths: List of paths to overlayed clip files
            output_path: Path for the merged output file

        Returns:
            Dict with merge metadata

        Raises:
            Exception: If merge fails
        """
        logger.info(f"Merging {len(overlayed_paths)} clips into {output_path}")

        try:
            # Use FFmpeg service's merge_videos method
            result = self.ffmpeg_service.merge_videos(
                input_paths=overlayed_paths,
                output_path=output_path
            )

            if not result.get('success'):
                raise Exception("FFmpeg merge failed")

            logger.info(f"Successfully merged {len(overlayed_paths)} clips")
            return result

        except Exception as e:
            logger.error(f"Merge failed: {str(e)}")
            raise Exception(f"Video merge failed: {str(e)}")

    def validate_merge_request(self, clip_configs: List[Dict]) -> None:
        """
        Validate merge request parameters

        Args:
            clip_configs: List of clip configurations

        Raises:
            ValueError: If validation fails
        """
        num_clips = len(clip_configs)

        # Check clip count
        if num_clips < 2:
            raise ValueError("At least 2 clips are required for merging")

        if num_clips > Config.MAX_MERGE_CLIPS:
            raise ValueError(f"Maximum {Config.MAX_MERGE_CLIPS} clips allowed per merge request")

        # Validate each clip config
        for i, config in enumerate(clip_configs):
            if not config.get('url'):
                raise ValueError(f"Clip {i+1}: URL is required")

            if not config.get('text'):
                raise ValueError(f"Clip {i+1}: Text is required")

            # Validate text length
            if len(config['text']) > 500:
                raise ValueError(f"Clip {i+1}: Text too long (max 500 characters)")

        logger.info(f"Validation passed for {num_clips} clips")

    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """Delete a temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {str(e)}")

    @staticmethod
    def cleanup_files(file_paths: List[str]) -> None:
        """Delete multiple temporary files"""
        for path in file_paths:
            MergeService.cleanup_file(path)

    async def process_merge_request(
        self,
        clip_configs: List[Dict],
        output_path: str
    ) -> Dict:
        """
        Main entry point: Download, overlay, and merge clips

        Args:
            clip_configs: List of clip configurations
            output_path: Path for final merged output

        Returns:
            Dict with processing metadata

        Raises:
            Exception: If any step fails
        """
        downloaded_paths = []
        overlayed_paths = []

        try:
            # Step 1: Validate request
            self.validate_merge_request(clip_configs)

            # Step 2: Download all clips
            clip_urls = [config['url'] for config in clip_configs]
            downloaded_clips = await self.download_clips(clip_urls)
            downloaded_paths = [path for path, _ in downloaded_clips]

            # Step 3: Apply overlays to each clip
            overlayed_paths = self.apply_overlays_to_clips(clip_configs, downloaded_clips)

            # Step 4: Cleanup downloaded originals (no longer needed)
            self.cleanup_files(downloaded_paths)
            downloaded_paths = []

            # Step 5: Merge all overlayed clips
            merge_result = self.merge_clips(overlayed_paths, output_path)

            # Step 6: Cleanup overlayed clips (no longer needed)
            self.cleanup_files(overlayed_paths)
            overlayed_paths = []

            return {
                'success': True,
                'clips_processed': len(clip_configs),
                'output_path': output_path,
                **merge_result
            }

        except Exception as e:
            # Cleanup on failure
            self.cleanup_files(downloaded_paths)
            self.cleanup_files(overlayed_paths)

            logger.error(f"Merge request processing failed: {str(e)}")
            raise


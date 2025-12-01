"""
FastAPI application for FFmpeg text overlay service
"""
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import os
import uuid
import logging
import time
import json
from pathlib import Path
from typing import Optional

from config import Config, list_templates
from models.schemas import (
    URLOverlayRequest, OverlayResponse, ErrorResponse,
    HealthResponse, TemplateListResponse, TextOverrideOptions,
    TemplateCreate, TemplateResponse, TemplateDuplicateRequest,
    MergeRequest, MergeResponse
)
from services.download_service import DownloadService
from services.ffmpeg_service import FFmpegService
from services.storage_service import StorageService
from services.auth_service import AuthService
from services.usage_service import UsageService
from services.template_service import TemplateService
from services.database_service import DatabaseService
from services.merge_service import MergeService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FFmpeg Text Overlay API",
    description="Add customizable text overlays to images and videos using FFmpeg",
    version="1.0.0"
)

# Auth Middleware
class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API keys on protected endpoints"""

    def __init__(self, app, auth_service: AuthService):
        super().__init__(app)
        self.auth_service = auth_service

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        public_paths = ["/", "/health", "/docs", "/openapi.json", "/redoc"]

        # Allow template endpoints without auth (for UI template editor)
        if request.url.path.startswith("/templates"):
            return await call_next(request)

        if request.url.path in public_paths:
            return await call_next(request)

        # Check for API key
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "status": "error",
                    "message": "Missing API key. Provide X-API-Key header or Authorization: Bearer <key>"
                }
            )

        # Validate API key
        user = self.auth_service.validate_api_key(api_key)
        if not user:
            return JSONResponse(
                status_code=401,
                content={
                    "status": "error",
                    "message": "Invalid or inactive API key"
                }
            )

        # Attach user to request state
        request.state.user = user
        request.state.user_id = user.id

        # Continue processing
        return await call_next(request)


# Add CORS middleware
# Configure CORS_ORIGINS environment variable for production (comma-separated list)
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
download_service = DownloadService()
ffmpeg_service = FFmpegService()
storage_service = StorageService()
auth_service = AuthService()
usage_service = UsageService()
template_service = TemplateService()
db_service = DatabaseService()

# Add auth middleware
app.add_middleware(APIKeyAuthMiddleware, auth_service=auth_service)

# Ensure temp directory exists
os.makedirs(Config.TEMP_DIR, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database and bootstrap default data on first startup"""
    try:
        # Initialize database tables
        logger.info("Initializing database tables...")
        db_service.init_templates_table()

        # Seed default template
        logger.info("Seeding default template...")
        template_service.seed_default_template()

        # Update default template font path (ensures production paths are correct)
        logger.info("Updating default template font path...")
        template_service.update_default_template_font_path()

        # Update default template font size
        logger.info("Updating default template font size...")
        template_service.update_default_template_font_size(46)

        # Bootstrap default user
        logger.info("Bootstrapping default user...")
        user, api_key = auth_service.bootstrap_default_user()
        if user and api_key:
            logger.info("=" * 60)
            logger.info("🎉 FIRST TIME SETUP COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"✓ User ID: {user.id}")
            logger.info(f"✓ API Key: {api_key}")
            logger.info("=" * 60)
            logger.info("⚠️  SAVE THIS API KEY - IT WON'T BE SHOWN AGAIN!")
            logger.info("=" * 60)
            logger.info("Add this to your n8n HTTP Request node:")
            logger.info(f'  Header: X-API-Key')
            logger.info(f'  Value: {api_key}')
            logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.warning("Application starting with limited functionality")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "FFmpeg Text Overlay API",
        "version": "1.0.0",
        "endpoints": {
            "POST /overlay/url": "Add text overlay from URL",
            "POST /overlay/upload": "Add text overlay from file upload",
            "GET /templates": "List available style templates",
            "GET /health": "Health check"
        },
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway"""
    ffmpeg_available = ffmpeg_service.check_ffmpeg_available()
    fonts_available = (
        ffmpeg_service.check_font_available(Config.INTER_REGULAR) and
        ffmpeg_service.check_font_available(Config.INTER_BOLD)
    )

    is_healthy = ffmpeg_available and fonts_available

    return HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        ffmpeg_available=ffmpeg_available,
        fonts_available=fonts_available,
        version="1.0.0"
    )


@app.post("/overlay/merge", response_model=MergeResponse)
async def merge_clips_with_overlays(
    request: MergeRequest,
    api_request: Request
):
    """
    Merge multiple video clips with text overlays

    This endpoint:
    1. Downloads all clips in parallel
    2. Applies text overlay to each clip
    3. Merges all overlayed clips into a single video
    4. Returns the merged video as a file download

    Limits:
    - 2-10 clips per request
    - Each clip: max 500 character text
    """
    start_time = time.time()
    user_id = api_request.state.user_id

    try:
        # Initialize services
        merge_service = MergeService()
        usage_service = UsageService()

        logger.info(f"Merge request for {len(request.clips)} clips from user {user_id}")

        # Generate output filename
        output_format = request.output_format
        output_filename = f"merged_{uuid.uuid4()}.{output_format}"
        output_path = os.path.join(Config.TEMP_DIR, output_filename)

        # Convert Pydantic models to dicts for merge service
        clip_configs = [
            {
                'url': str(clip.url),
                'text': clip.text,
                'template': clip.template,
                'overrides': clip.overrides.model_dump() if clip.overrides else None
            }
            for clip in request.clips
        ]

        # Process merge request (download, trim if requested, overlay, merge)
        result = await merge_service.process_merge_request(
            clip_configs=clip_configs,
            output_path=output_path,
            first_clip_duration=request.first_clip_duration,
            first_clip_trim_mode=request.first_clip_trim_mode or "both"
        )

        processing_time = time.time() - start_time
        processing_time_ms = int(processing_time * 1000)

        logger.info(f"Merge completed in {processing_time:.2f}s")

        # Track usage
        output_size = os.path.getsize(output_path)
        usage_service.track_usage(
            user_id=user_id,
            endpoint="/overlay/merge",
            input_file_size_bytes=0,  # Multiple downloads tracked internally
            output_file_size_bytes=output_size,
            processing_time_ms=processing_time_ms,
            template_used="multiple",
            has_custom_overrides=any(clip.overrides for clip in request.clips)
        )

        # Handle response format
        if request.response_format == "url":
            # Upload to R2 and return URL
            if not storage_service.enabled:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="R2 storage is not enabled. Set R2_ENABLED=true in environment."
                )

            r2_url = await storage_service.upload_file(
                file_path=output_path,
                object_name=None,
                user_id=None,
                file_type="outputs",
                public=True
            )

            if not r2_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload to R2 storage"
                )

            # Cleanup temp file
            download_service.cleanup_file(output_path)

            # Return JSON with URL
            return JSONResponse(
                content=MergeResponse(
                    status="success",
                    message=f"Successfully merged {len(request.clips)} clips",
                    filename=output_filename,
                    download_url=r2_url,
                    clips_processed=len(request.clips),
                    processing_time=processing_time,
                    total_duration=result.get('duration')
                ).model_dump()
            )
        else:
            # Default: Return binary file
            return FileResponse(
                path=output_path,
                filename=output_filename,
                media_type=f"video/{output_format}",
                background=_cleanup_files([output_path])
            )

    except ValueError as e:
        logger.error(f"Validation error in merge request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing merge request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Merge processing failed: {str(e)}"
        )


@app.get("/templates", response_model=TemplateListResponse)
async def get_templates():
    """Get list of available style templates"""
    templates = list_templates()
    return TemplateListResponse(
        templates=templates,
        count=len(templates)
    )


@app.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(template: TemplateCreate, request: Request):
    """
    Create a new template

    Requires authentication via API key.
    """
    try:
        # Add font_path based on Config (frontend doesn't send this)
        template_data = template.model_dump()
        template_data['font_path'] = Config.TIKTOK_SANS_SEMIBOLD  # Default font

        created = template_service.create_template(template_data)

        # Convert datetime objects to strings for response
        created['created_at'] = str(created['created_at'])
        created['updated_at'] = str(created['updated_at'])

        return TemplateResponse(**created)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create template")


@app.get("/templates/{name}", response_model=TemplateResponse)
async def get_template(name: str):
    """Get a specific template by name"""
    template = template_service.get_template(name)

    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Template '{name}' not found")

    # Convert datetime objects to strings
    template['created_at'] = str(template['created_at'])
    template['updated_at'] = str(template['updated_at'])

    return TemplateResponse(**template)


@app.put("/templates/{name}", response_model=TemplateResponse)
async def update_template(name: str, template: TemplateCreate, request: Request):
    """
    Update an existing template

    Requires authentication via API key.
    """
    try:
        template_data = template.model_dump(exclude_none=True)

        # Update font_path if needed
        if 'font_path' not in template_data:
            template_data['font_path'] = Config.TIKTOK_SANS_SEMIBOLD

        updated = template_service.update_template(name, template_data)

        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Template '{name}' not found")

        # Convert datetime objects to strings
        updated['created_at'] = str(updated['created_at'])
        updated['updated_at'] = str(updated['updated_at'])

        return TemplateResponse(**updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update template: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update template")


@app.delete("/templates/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(name: str, request: Request):
    """
    Delete a template

    Requires authentication via API key.
    Cannot delete the default template.
    """
    try:
        deleted = template_service.delete_template(name)

        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Template '{name}' not found")

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete template: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete template")


@app.post("/templates/{name}/duplicate", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_template(name: str, duplicate_request: TemplateDuplicateRequest, request: Request):
    """
    Duplicate an existing template

    Requires authentication via API key.
    """
    try:
        duplicated = template_service.duplicate_template(name, duplicate_request.new_name)

        # Convert datetime objects to strings
        duplicated['created_at'] = str(duplicated['created_at'])
        duplicated['updated_at'] = str(duplicated['updated_at'])

        return TemplateResponse(**duplicated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to duplicate template: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to duplicate template")


@app.post("/overlay/url", response_model=OverlayResponse)
async def overlay_from_url(request: URLOverlayRequest, http_request: Request):
    """
    Add text overlay to image/video from URL (primary method)

    This is the main endpoint for processing files hosted on Cloudflare R2 or other URLs.
    """
    input_path = None
    output_path = None
    start_time = time.time()
    user_id = getattr(http_request.state, "user_id", "unknown")

    try:
        logger.info(f"Processing overlay request from URL: {request.url}")

        # Download file from URL
        input_path, content_type = await download_service.download_from_url(str(request.url))
        logger.info(f"Downloaded file: {input_path} ({content_type})")

        # Validate file extension
        if not download_service.validate_file_extension(input_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type"
            )

        # Determine output format
        output_ext = Path(input_path).suffix
        if request.output_format != "same":
            output_ext = f".{request.output_format}"

        # Generate output filename
        output_filename = f"{uuid.uuid4()}{output_ext}"
        output_path = os.path.join(Config.TEMP_DIR, output_filename)

        # Process with FFmpeg
        result = ffmpeg_service.add_text_overlay(
            input_path=input_path,
            output_path=output_path,
            text=request.text,
            template_name=request.template,
            overrides=request.overrides
        )

        processing_time = time.time() - start_time
        processing_time_ms = int(processing_time * 1000)
        logger.info(f"Processing completed in {processing_time:.2f}s")

        # Get file sizes
        input_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)

        # Track usage
        usage_service.track_usage(
            user_id=user_id,
            endpoint="/overlay/url",
            input_file_size_bytes=input_size,
            output_file_size_bytes=output_size,
            processing_time_ms=processing_time_ms,
            template_used=request.template,
            has_custom_overrides=request.overrides is not None
        )

        # Handle response format
        if request.response_format == "url":
            # Upload to R2 and return URL
            if not storage_service.enabled:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="R2 storage is not enabled. Set R2_ENABLED=true in environment."
                )

            r2_url = await storage_service.upload_file(
                file_path=output_path,
                object_name=None,
                user_id=None,
                file_type="outputs",
                public=True
            )

            if not r2_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload to R2 storage"
                )

            # Cleanup temp files
            download_service.cleanup_file(input_path)
            download_service.cleanup_file(output_path)

            # Return JSON with URL
            return JSONResponse(
                content=OverlayResponse(
                    status="success",
                    message="Overlay applied successfully",
                    filename=output_filename,
                    download_url=r2_url,
                    processing_time=processing_time
                ).model_dump()
            )
        else:
            # Default: Return binary file
            return FileResponse(
                path=output_path,
                filename=output_filename,
                media_type=content_type,
                background=_cleanup_files([input_path, output_path])
            )

    except Exception as e:
        # Cleanup on error
        if input_path and os.path.exists(input_path):
            download_service.cleanup_file(input_path)
        if output_path and os.path.exists(output_path):
            download_service.cleanup_file(output_path)

        logger.error(f"Error processing overlay: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/overlay/upload", response_model=OverlayResponse)
async def overlay_from_upload(
    file: UploadFile = File(...),
    text: str = Form(...),
    template: str = Form("default"),
    overrides: Optional[str] = Form(None),
    output_format: str = Form("same"),
    response_format: str = Form("binary"),
    http_request: Request = None
):
    """
    Add text overlay to uploaded image/video (backup method)

    Use this endpoint when files are not already hosted on a CDN.
    """
    input_path = None
    output_path = None
    start_time = time.time()
    user_id = getattr(http_request.state, "user_id", "unknown")

    try:
        logger.info(f"Processing overlay request from upload: {file.filename}")

        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            )

        # Check content type
        if file.content_type not in Config.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type: {file.content_type}"
            )

        # Save uploaded file
        input_filename = f"{uuid.uuid4()}{file_ext}"
        input_path = os.path.join(Config.TEMP_DIR, input_filename)

        # Read and save file in chunks
        total_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks

        with open(input_path, 'wb') as f:
            while chunk := await file.read(chunk_size):
                total_size += len(chunk)
                if total_size > Config.MAX_FILE_SIZE:
                    f.close()
                    os.remove(input_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large. Max size: {Config.MAX_FILE_SIZE} bytes"
                    )
                f.write(chunk)

        logger.info(f"Saved uploaded file: {input_path} ({total_size} bytes)")

        # Parse overrides if provided
        override_options = None
        if overrides:
            try:
                override_dict = json.loads(overrides)
                override_options = TextOverrideOptions(**override_dict)
            except Exception as e:
                logger.warning(f"Failed to parse overrides: {str(e)}")

        # Validate template
        # Validate template exists in database
        if not template_service.template_exists(template):
            logger.warning(f"Template '{template}' not found, using default")
            template = "default"

        # Determine output format
        output_ext = file_ext
        if output_format != "same":
            output_ext = f".{output_format}"

        # Generate output filename
        output_filename = f"{uuid.uuid4()}{output_ext}"
        output_path = os.path.join(Config.TEMP_DIR, output_filename)

        # Process with FFmpeg
        result = ffmpeg_service.add_text_overlay(
            input_path=input_path,
            output_path=output_path,
            text=text,
            template_name=template,
            overrides=override_options
        )

        processing_time = time.time() - start_time
        processing_time_ms = int(processing_time * 1000)
        logger.info(f"Processing completed in {processing_time:.2f}s")

        # Get file sizes
        input_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)

        # Track usage
        usage_service.track_usage(
            user_id=user_id,
            endpoint="/overlay/upload",
            input_file_size_bytes=input_size,
            output_file_size_bytes=output_size,
            processing_time_ms=processing_time_ms,
            template_used=template,
            has_custom_overrides=override_options is not None
        )

        # Handle response format
        if response_format == "url":
            # Upload to R2 and return URL
            if not storage_service.enabled:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="R2 storage is not enabled. Set R2_ENABLED=true in environment."
                )

            r2_url = await storage_service.upload_file(
                file_path=output_path,
                object_name=None,
                user_id=None,
                file_type="outputs",
                public=True
            )

            if not r2_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload to R2 storage"
                )

            # Cleanup temp files
            download_service.cleanup_file(input_path)
            download_service.cleanup_file(output_path)

            # Return JSON with URL
            return JSONResponse(
                content=OverlayResponse(
                    status="success",
                    message="Overlay applied successfully",
                    filename=output_filename,
                    download_url=r2_url,
                    processing_time=processing_time
                ).model_dump()
            )
        else:
            # Default: Return binary file
            return FileResponse(
                path=output_path,
                filename=output_filename,
                media_type=file.content_type,
                background=_cleanup_files([input_path, output_path])
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Cleanup on error
        if input_path and os.path.exists(input_path):
            download_service.cleanup_file(input_path)
        if output_path and os.path.exists(output_path):
            download_service.cleanup_file(output_path)

        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def _cleanup_files(file_paths: list):
    """Background task to cleanup temporary files"""
    async def cleanup():
        import asyncio
        await asyncio.sleep(1)  # Wait a bit to ensure file was sent
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"Cleaned up: {path}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup {path}: {str(e)}")

    return cleanup


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status="error",
            message=exc.detail
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            status="error",
            message="Internal server error"
        ).model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

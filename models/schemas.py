"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, Literal, List
import re


class TextOverrideOptions(BaseModel):
    """Optional overrides for text styling"""
    font_family: Optional[Literal["regular", "bold"]] = None  # Deprecated, use font_weight instead
    font_weight: Optional[int] = Field(None, ge=100, le=900)
    font_size: Optional[int] = Field(None, ge=12, le=200)
    text_color: Optional[str] = None
    border_width: Optional[int] = Field(None, ge=0, le=10)
    border_color: Optional[str] = None
    shadow_x: Optional[int] = Field(None, ge=-20, le=20)
    shadow_y: Optional[int] = Field(None, ge=-20, le=20)
    shadow_color: Optional[str] = None
    background_enabled: Optional[bool] = None
    background_color: Optional[str] = None
    background_opacity: Optional[float] = Field(None, ge=0.0, le=1.0)
    text_opacity: Optional[float] = Field(None, ge=0.0, le=1.0)
    position: Optional[Literal["center", "top-left", "top-right", "top-center",
                                "bottom-left", "bottom-right", "bottom-center",
                                "middle-left", "middle-right", "custom"]] = None
    custom_x: Optional[int] = Field(None, ge=0)
    custom_y: Optional[int] = Field(None, ge=0)
    alignment: Optional[Literal["left", "center", "right"]] = None
    max_text_width_percent: Optional[int] = Field(None, ge=10, le=100)
    line_spacing: Optional[int] = Field(None, ge=-50, le=50)  # Negative for tighter spacing

    @field_validator("text_color", "border_color", "shadow_color", "background_color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color format (hex or named colors)"""
        if v is None:
            return v

        valid_named_colors = [
            "white", "black", "red", "green", "blue", "yellow",
            "cyan", "magenta", "orange", "purple", "pink", "gray", "grey"
        ]

        if v.lower() in valid_named_colors:
            return v.lower()

        # Validate hex format
        if re.match(r'^#?[0-9A-Fa-f]{6}$', v):
            return v if v.startswith('#') else f'#{v}'

        raise ValueError(f"Invalid color format: {v}. Use hex (#RRGGBB) or named colors")

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: Optional[str], info) -> Optional[str]:
        """Validate position requirements"""
        if v == "custom":
            # Custom position requires custom_x and custom_y
            # Note: We can't access other fields here, validation happens in endpoint
            pass
        return v


class URLOverlayRequest(BaseModel):
    """Request model for URL-based overlay"""
    url: HttpUrl
    text: str = Field(..., min_length=1, max_length=500)
    template: Optional[Literal["default"]] = "default"
    overrides: Optional[TextOverrideOptions] = None
    output_format: Optional[Literal["same", "mp4", "jpg", "png"]] = "same"
    response_format: Optional[Literal["binary", "url"]] = "binary"

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Sanitize text to prevent command injection"""
        # Remove potentially dangerous characters for shell
        # Allow newlines for multi-line text support
        # Include all quote variants: straight, smart/curly (both single and double)
        dangerous_chars = ['`', '$', '"', '"', '"', "'", ''', ''']
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v.strip()


class UploadOverlayRequest(BaseModel):
    """Request model for file upload overlay (form data)"""
    text: str = Field(..., min_length=1, max_length=500)
    template: Optional[Literal["default"]] = "default"
    overrides: Optional[str] = None  # JSON string of TextOverrideOptions
    output_format: Optional[Literal["same", "mp4", "jpg", "png"]] = "same"
    response_format: Optional[Literal["binary", "url"]] = "binary"

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Sanitize text to prevent command injection"""
        # Allow newlines for multi-line text support
        dangerous_chars = ['`', '$', '"']  # Removed \n and \r
        for char in dangerous_chars:
            v = v.replace(char, '')
        return v.strip()


class OverlayResponse(BaseModel):
    """Response model for overlay operations"""
    status: Literal["success", "error"]
    message: str
    filename: Optional[str] = None
    download_url: Optional[str] = None
    processing_time: Optional[float] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    status: Literal["error"]
    message: str
    details: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: Literal["healthy", "unhealthy"]
    ffmpeg_available: bool
    fonts_available: bool
    version: str


class TemplateListResponse(BaseModel):
    """Template list response"""
    templates: dict
    count: int


class TemplateCreate(BaseModel):
    """Schema for creating a template"""
    name: str = Field(..., min_length=1, max_length=100)
    font_size: int = Field(..., ge=12, le=200)
    font_weight: int = Field(default=500, ge=100, le=900)
    text_color: str
    border_width: int = Field(..., ge=0, le=10)
    border_color: str
    shadow_x: int = Field(..., ge=-20, le=20)
    shadow_y: int = Field(..., ge=-20, le=20)
    shadow_color: str
    position: str
    background_enabled: bool
    background_color: str
    background_opacity: float = Field(..., ge=0.0, le=1.0)
    text_opacity: float = Field(..., ge=0.0, le=1.0)
    alignment: Literal["left", "center", "right"] = "center"
    max_text_width_percent: int = Field(default=80, ge=10, le=100)
    line_spacing: int = Field(default=-8, ge=-50, le=50)

    @field_validator("text_color", "border_color", "shadow_color", "background_color")
    @classmethod
    def validate_template_color(cls, v: str) -> str:
        """Validate color format (hex or named colors)"""
        valid_named_colors = [
            "white", "black", "red", "green", "blue", "yellow",
            "cyan", "magenta", "orange", "purple", "pink", "gray", "grey"
        ]

        if v.lower() in valid_named_colors:
            return v.lower()

        # Validate hex format
        if re.match(r'^#?[0-9A-Fa-f]{6}$', v):
            return v if v.startswith('#') else f'#{v}'

        raise ValueError(f"Invalid color format: {v}. Use hex (#RRGGBB) or named colors")


class TemplateResponse(BaseModel):
    """Schema for template response"""
    name: str
    font_path: str
    font_size: int
    font_weight: int
    text_color: str
    border_width: int
    border_color: str
    shadow_x: int
    shadow_y: int
    shadow_color: str
    position: str
    background_enabled: bool
    background_color: str
    background_opacity: float
    text_opacity: float
    alignment: str
    max_text_width_percent: int
    line_spacing: int
    created_at: str
    updated_at: str
    is_default: bool


class TemplateDuplicateRequest(BaseModel):
    """Schema for duplicating template"""
    new_name: str = Field(..., min_length=1, max_length=100)


class ClipConfig(BaseModel):
    """Configuration for a single clip in merge request"""
    url: HttpUrl
    text: str = Field(..., min_length=1, max_length=500)
    template: str = "default"
    overrides: Optional[TextOverrideOptions] = None


class MergeRequest(BaseModel):
    """Request model for merging multiple clips with overlays"""
    clips: List[ClipConfig] = Field(..., min_length=2, max_length=10, description="2-10 clips to merge")
    output_format: Literal["mp4", "mov"] = "mp4"
    response_format: Optional[Literal["binary", "url"]] = "binary"

    # First clip trimming options
    first_clip_duration: Optional[float] = Field(
        None,
        gt=0,
        le=300,
        description="Target duration in seconds for the first clip. If not set, uses full clip length."
    )
    first_clip_trim_mode: Optional[Literal["start", "end", "both"]] = Field(
        "both",
        description="Where to trim from: 'start' (remove from beginning), 'end' (remove from end), 'both' (split equally)"
    )


class MergeResponse(BaseModel):
    """Response model for merge operations"""
    status: Literal["success", "error"]
    message: str
    filename: Optional[str] = None
    download_url: Optional[str] = None
    clips_processed: Optional[int] = None
    processing_time: Optional[float] = None
    total_duration: Optional[float] = None

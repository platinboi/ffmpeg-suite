import logging
from typing import Optional, List
from rembg import remove, new_session


class RembgService:
    """Wrapper around rembg with model session caching and tunable parameters."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sessions = {}  # Cache sessions per model

    def get_session(self, model: str):
        """Get or create a session for the specified model."""
        if model not in self.sessions:
            self.logger.info(f"Loading rembg model: {model}")
            self.sessions[model] = new_session(model)
        return self.sessions[model]

    def remove_background(
        self,
        input_path: str,
        output_path: str,
        model: str = "u2net",
        alpha_matting: bool = False,
        foreground_threshold: int = 240,
        background_threshold: int = 10,
        erode_size: int = 10,
        post_process_mask: bool = False,
        bgcolor: Optional[List[int]] = None
    ) -> None:
        """Remove background from image with configurable parameters."""
        session = self.get_session(model)

        with open(input_path, "rb") as f:
            data = f.read()

        result = remove(
            data,
            session=session,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=foreground_threshold,
            alpha_matting_background_threshold=background_threshold,
            alpha_matting_erode_size=erode_size,
            post_process_mask=post_process_mask,
            bgcolor=tuple(bgcolor) if bgcolor else None
        )

        with open(output_path, "wb") as f:
            f.write(result)

        self.logger.info(f"Background removed (model={model}, alpha={alpha_matting}) -> {output_path}")


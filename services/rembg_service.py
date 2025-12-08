import logging
from rembg import remove, new_session


class RembgService:
    """Lightweight wrapper around rembg with a cached session."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = new_session()

    def remove_background(self, input_path: str, output_path: str) -> None:
        """Remove background from image at input_path and write PNG to output_path."""
        with open(input_path, "rb") as i:
            data = i.read()
        result = remove(data, session=self.session)
        with open(output_path, "wb") as o:
            o.write(result)
        self.logger.info("Background removed -> %s", output_path)


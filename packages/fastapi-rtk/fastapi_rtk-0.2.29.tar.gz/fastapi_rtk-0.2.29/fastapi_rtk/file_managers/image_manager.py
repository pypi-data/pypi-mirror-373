from ..bases.file_manager import AbstractImageManager
from ..setting import Setting
from ..utils import lazy
from .file_manager import FileManager

__all__ = ["ImageManager"]


class ImageManager(FileManager, AbstractImageManager):
    """
    ImageManager is a specialized FileManager for handling image files.
    """

    base_path = lazy(lambda: Setting.IMG_UPLOAD_FOLDER)
    allowed_extensions = lazy(lambda: Setting.IMG_ALLOWED_EXTENSIONS)

    def post_init(self):
        if not self.base_path:
            raise ValueError("IMG_UPLOAD_FOLDER not set in config.")

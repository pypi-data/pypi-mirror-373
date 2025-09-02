from ..bases.file_manager import AbstractImageManager
from .s3_file_manager import S3FileManager

__all__ = ["S3ImageManager"]


class S3ImageManager(S3FileManager, AbstractImageManager):
    """
    S3ImageManager is a specialized S3FileManager for handling image files.
    It inherits from S3FileManager and implements AbstractImageManager.
    """

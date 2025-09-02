from ..bases.file_manager import AbstractFileManager
from ..const import logger

__all__ = ["S3FileManager"]


class S3FileManager(AbstractFileManager):
    """
    FileManager for handling files in S3 buckets.
    """

    def __init__(
        self,
        base_path=None,
        allowed_extensions=None,
        namegen=None,
        permission=None,
        bucket_name=None,
        bucket_subfolder=None,
        access_key=None,
        secret_key=None,
    ):
        super().__init__(base_path, allowed_extensions, namegen, permission)
        self.bucket_name = bucket_name
        self.bucket_subfolder = bucket_subfolder
        self.access_key = access_key
        self.secret_key = secret_key

        if not self.bucket_name:
            logger.warning(
                f"Bucket name is not set for {self.__class__.__name__}. "
                "Files may not be able to be deleted"
            )

        if not self.access_key or not self.secret_key:
            logger.warning(
                f"Access key or secret key is not set for {self.__class__.__name__}. "
                "Files may not be able to be deleted"
            )

        try:
            import boto3
            import smart_open

            self.smart_open = smart_open
            self.boto3 = boto3
        except ImportError:
            raise ImportError(
                "smart_open is required for S3FileManager. "
                "Please install it with 'pip install smart_open[s3]'."
            )

    def get_path(self, filename):
        return self.base_path + "/" + filename

    def get_file(self, filename):
        with self.smart_open.open(self.get_path(filename), "rb") as f:
            return f.read()

    async def stream_file(self, filename):
        with self.smart_open.open(self.get_path(filename), "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    def save_file(self, file_data, filename):
        with self.smart_open.open(self.get_path(filename), "wb") as f:
            f.write(file_data.file.read())

    def save_content_to_file(self, content, filename):
        with self.smart_open.open(self.get_path(filename), "wb") as f:
            f.write(content)

    def delete_file(self, filename):
        path = self.get_path(filename)
        try:
            self.smart_open.open(path, "rb").close()  # Check if file exists
            s3 = self.boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            s3.delete_object(
                Bucket=self.bucket_name,
                Key=f"{self.bucket_subfolder}/{filename}"
                if self.bucket_subfolder
                else filename,
            )
        except FileNotFoundError:
            pass

    def file_exists(self, filename):
        path = self.get_path(filename)
        try:
            with self.smart_open.open(path, "rb"):
                return True
        except FileNotFoundError:
            return False

    def get_instance_with_subfolder(self, subfolder, *args, **kwargs):
        return super().get_instance_with_subfolder(
            subfolder,
            bucket_name=self.bucket_name,
            bucket_subfolder=f"{self.bucket_subfolder}/{subfolder}"
            if self.bucket_subfolder
            else subfolder,
            access_key=self.access_key,
            secret_key=self.secret_key,
            *args,
            **kwargs,
        )

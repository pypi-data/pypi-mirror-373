import abc
import typing

import fastapi

from ..utils import lazy, uuid_namegen


class AbstractFileManager(abc.ABC):
    """
    Abstract base class for file managers.
    """

    base_path = None
    allowed_extensions = None
    namegen = lazy(lambda: uuid_namegen)
    permission = lazy(lambda: 0o755)

    def __init__(
        self,
        base_path: str | None = None,
        allowed_extensions: list[str] | None = None,
        namegen: typing.Callable[[str], str] | None = None,
        permission: int | None = None,
    ):
        if base_path is not None:
            self.base_path = base_path
        if allowed_extensions is not None:
            self.allowed_extensions = allowed_extensions
        if namegen is not None:
            self.namegen = namegen
        if permission is not None:
            self.permission = permission

        self.post_init()

        if not self.base_path:
            raise ValueError(f"`base_path` must be set for {self.__class__.__name__}.")

        # Ensure base_path does not end with a slash
        self.base_path = self.base_path.rstrip("/")

    """
    --------------------------------------------------------------------------------------------------------
        CRUD METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    @abc.abstractmethod
    def get_path(self, filename: str) -> str:
        """
        Gets the full path of a file by its filename.

        Args:
            filename (str): The name of the file.

        Returns:
            str: The full path of the file.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def get_file(self, filename: str) -> bytes | str:
        """
        Gets the content of a file by its filename.

        Args:
            filename (str): The name of the file.

        Returns:
            bytes | str: The content of the file.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    async def stream_file(
        self, filename: str
    ) -> typing.Generator[bytes | str, None, None]:
        """
        Streams a file's content as a generator.

        Args:
            filename (str): The name of the file to stream.

        Returns:
            typing.Generator[bytes | str, None, None]: A generator that yields the file's content.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def save_file(self, file_data: fastapi.UploadFile, filename: str) -> str:
        """
        Saves a file to the filesystem. Assumes `filename` is already unique, but not yet secured.

        Args:
            file_data (fastapi.UploadFile): The file data to save.
            filename (str): The name of the file to save.

        Returns:
            str: The path where the file was saved.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def save_content_to_file(self, content: bytes | str, filename: str) -> str:
        """
        Saves content to a file in the filesystem. Assumes `filename` is already unique, but not yet secured.

        Args:
            content (bytes | str): The content to save.
            filename (str): The name of the file to save.

        Returns:
            str: The path where the content was saved.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def delete_file(self, filename: str) -> None:
        """
        Deletes a file from the filesystem.

        Args:
            filename (str): The name of the file to delete.

        Returns:
            None
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abc.abstractmethod
    def file_exists(self, filename: str) -> bool:
        """
        Checks if a file exists in the filesystem. Assumes `filename` is already unique, but not yet secured.

        Args:
            filename (str): The name of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    """
    --------------------------------------------------------------------------------------------------------
        PRE AND POST METHODS - can be implemented
    --------------------------------------------------------------------------------------------------------
    """

    def post_init(self):
        """
        Post-initialization method that can be overridden by subclasses.
        This method is called after the instance is created and initialized.
        """
        pass

    """
    --------------------------------------------------------------------------------------------------------
        UTILITY METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    def get_instance_with_subfolder(self, subfolder: str, *args, **kwargs):
        """
        Returns a new instance of this class with a modified base path.

        Args:
            subfolder (str): The subfolder to append to the base path.
            *args: Additional positional arguments to pass to the constructor.
            **kwargs: Additional keyword arguments to pass to the constructor.

        Returns:
            AbstractFileManager: A new instance of this class with the modified base path.
        """
        return self.__class__(
            base_path=f"{self.base_path}/{subfolder}",
            allowed_extensions=self.allowed_extensions,
            namegen=self.namegen,
            permission=self.permission,
            *args,
            **kwargs,
        )

    def is_filename_allowed(self, filename: str) -> bool:
        """
        Check if a file is allowed based on its extension.

        Args:
            filename (str): The name of the file.

        Returns:
            bool: True if the file is allowed, False otherwise.
        """
        if self.allowed_extensions is None:
            return True

        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        )

    def generate_name(self, filename: str) -> str:
        """
        Generates a name for the given file data.

        Args:
            filename (str): The name of the file to generate a name for.

        Returns:
            str: The generated name for the file.
        """
        return self.namegen(filename)


class AbstractImageManager(AbstractFileManager):
    """
    Abstract base class for image managers.
    """

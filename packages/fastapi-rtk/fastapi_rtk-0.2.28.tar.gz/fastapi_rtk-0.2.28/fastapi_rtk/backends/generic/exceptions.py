from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import GenericColumn, GenericModel

__all__ = [
    "GenericColumnException",
    "PKMultipleException",
    "PKMissingException",
    "ColumnNotSetException",
    "ColumnInvalidTypeException",
    "MultipleColumnsException",
]


class BaseGenericException(Exception):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)})"


class GenericColumnException(BaseGenericException):
    column: "GenericColumn"
    message: str

    def __init__(
        self,
        column: "GenericColumn",
        message: str,
    ) -> None:
        self.column = column
        self.message = message

    def __repr__(self):
        return f"{self.message} for column {self.column}"


class GenericModelClassException(BaseGenericException):
    model_name: str
    message: str

    def __init__(
        self,
        model_name: str,
        message: str,
    ) -> None:
        self.model_name = model_name
        self.message = message

    def __repr__(self):
        return f"{self.message} for model {self.model_name}"


class GenericModelException(BaseGenericException):
    model: "GenericModel"
    message: str

    def __init__(
        self,
        model: "GenericModel",
        message: str,
    ) -> None:
        self.model = model
        self.message = message

    def __repr__(self):
        return f"{self.message} for model {str(self.model)}"


class PKMultipleException(GenericModelClassException):
    pass


class PKMissingException(GenericModelClassException):
    pass


class ColumnNotSetException(GenericModelException):
    pass


class ColumnInvalidTypeException(GenericModelException):
    pass


class MultipleColumnsException(GenericModelException):
    errors: list[GenericModelException]

    def __init__(
        self, model: "GenericModel", errors: list[GenericModelException]
    ) -> None:
        super().__init__(model, "")
        self.errors = errors
        self.message = ",".join([e.message for e in errors])

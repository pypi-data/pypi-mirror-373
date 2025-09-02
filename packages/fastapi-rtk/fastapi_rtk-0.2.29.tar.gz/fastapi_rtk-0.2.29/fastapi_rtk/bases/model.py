class BasicModel:
    """
    A basic model class that provides a method to update the model instance with the given data.
    """

    def update(self, data: dict[str, any]):
        """
        Updates the model instance with the given data.

        Args:
            data (dict): The data to update the model instance with.

        Returns:
            None
        """
        for key, value in data.items():
            setattr(self, key, value)

    @property
    def name_(self):
        """
        Returns the string representation of the object.
        """
        return str(self)

    @property
    def id_(self):
        """
        Returns the primary keys of the model instance.

        Returns:
            list[str] | str: A list of primary key values or a single primary key value if there is only one.
        """
        pks: list[str] | str = [str(getattr(self, pk)) for pk in self.get_pk_attrs()]
        if len(pks) == 1:
            pks = pks[0]
        return pks

    """
    --------------------------------------------------------------------------------------------------------
        GET METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    @classmethod
    def get_pk_attrs(cls) -> list[str]:
        """
        Get the primary key attributes of the model.

        This method should be implemented by subclasses to return a list of primary key attribute names.

        Returns:
            list[str]: A list of primary key attribute names.
        """
        raise NotImplementedError("Subclasses must implement this method.")

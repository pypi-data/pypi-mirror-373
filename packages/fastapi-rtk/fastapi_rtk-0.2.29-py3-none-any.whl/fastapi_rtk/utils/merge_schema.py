import secrets
import typing

import pydantic

__all__ = ["merge_schema"]


def merge_schema(
    schema: pydantic.BaseModel,
    fields: typing.Dict[str, tuple[type, pydantic.fields.FieldInfo]],
    only_update=False,
    name: str | None = None,
) -> typing.Type[pydantic.BaseModel]:
    """
    Replace or add fields to the given schema.

    Args:
        schema (BaseModel): The schema to be updated.
        fields (Dict[str, tuple[type, Field]]): The fields to be added or updated.
        only_update (bool): If True, only update the fields with the same name. Otherwise, add new fields.
        name (str, optional): The name of the new schema. If not given, the schema name will be suffixed with a random hex string. Defaults to None.

    Returns:
        BaseModel: The updated schema.
    """
    name = name or f"{schema.__name__}-{secrets.token_hex(3)}"
    new_fields = dict()
    if only_update:
        for key, value in schema.model_fields.items():
            if key in fields:
                val = fields[key]
                if isinstance(val, tuple):
                    new_fields[key] = val
                else:
                    new_fields[key] = (value.annotation, val)
    else:
        new_fields = fields

    return pydantic.create_model(
        name,
        **new_fields,
        __base__=schema,
    )

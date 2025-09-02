import copy
import typing

__all__ = ["deep_merge"]


def deep_merge(
    *data: typing.Dict[str, typing.Any],
    rules: typing.Dict[str, typing.Callable[[typing.Any, typing.Any], bool]]
    | None = None,
):
    """
    Recursively merges multiple dictionaries into the first one.

    - If the key does not exist in the previous dictionary, it will be directly added.
    - If previous key is a dictionary and the next key is also a dictionary, it will recursively merge them.
    - If previous key is a list and the next key is also a list, it will concatenate the lists.
    - If the key exists in `rules`, it will apply the rule to determine if the value should be overwritten.

    Args:
        data (typing.Dict[str, typing.Any]): A variable number of dictionaries to be merged. The first dictionary will be deep-copied and used as the base dictionary, while the subsequent dictionaries will be merged into it.
        rules (typing.Dict[str, typing.Callable[[typing.Any, typing.Any], bool]] | None, optional): A dictionary of rules to apply when merging values. If a key in the `rules` corresponds to a key in the `data`, the rule will be applied to determine if the value should be overwritten. The rule should be a callable that takes two arguments: the existing value and the new value, and returns a boolean indicating whether to overwrite the existing value. Defaults to None.

    Returns:
        typing.Dict[str, typing.Any]: The merged dictionary containing all keys and values from the input dictionaries, with the first dictionary as the base. The merging process respects the rules defined in the `rules` parameter, if provided.
    """
    base_data, *data = data
    base_data = copy.deepcopy(base_data)
    for dat in data:
        for key, value in dat.items():
            if key not in base_data:
                base_data[key] = value
                continue

            if isinstance(value, dict) and isinstance(base_data[key], dict):
                base_data[key] = deep_merge(base_data[key], value, rules=rules)
            elif isinstance(value, list) and isinstance(base_data[key], list):
                base_data[key].extend(x for x in value if x not in base_data[key])
            elif rules and key in rules:
                if rules[key](base_data[key], value):
                    base_data[key] = value
            else:
                base_data[key] = value

    return base_data

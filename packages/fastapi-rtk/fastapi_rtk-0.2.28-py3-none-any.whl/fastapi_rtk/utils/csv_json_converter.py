import csv
import enum
import json
import typing

from ..types import ExportMode

__all__ = ["Line", "CSVJSONConverter"]


class Line:
    _line = ""

    def write(self, line: str):
        self._line = line

    def read(self):
        return self._line


class CSVJSONConverter:
    """
    A utility class for converting CSV data to JSON format and vice versa.
    """

    @classmethod
    def csv_to_json(
        cls,
        csv_data: str | bytes,
        *,
        delimiter=",",
        quotechar: str | None = None,
    ):
        """
        Converts CSV data to JSON format.

        Args:
            csv_data (str, bytes): The CSV data.
            delimiter (str, optional): The delimiter to use in the CSV. Defaults to ",".
            quotechar (str | None, optional): Quote character for the CSV file. If not given, it will not be used. Defaults to None.

        Returns:
            list[dict[str, Any]]: The JSON data as a list of dictionaries.
        """
        if isinstance(csv_data, bytes):
            csv_data = csv_data.decode("utf-8")

        lines = csv_data.splitlines()
        reader = csv.DictReader(lines, delimiter=delimiter, quotechar=quotechar)
        return [
            cls._convert_nested_col_into_dict(
                row, list_delimiter=";" if delimiter != ";" else ","
            )
            for row in reader
        ]

    @classmethod
    def json_to_csv(
        cls,
        data: dict[str, typing.Any] | list[dict[str, typing.Any]],
        /,
        *,
        list_columns: list[str],
        label_columns: dict[str, str],
        with_header=True,
        delimiter=",",
        quotechar: str | None = None,
        relation_separator: str = ".",
        export_mode: ExportMode = "simplified",
    ):
        """
        Converts JSON data to CSV format.

        Args:
            data (dict[str, Any] | list[dict[str, Any]]): The JSON data to be converted.
            list_columns (list[str]): The list of columns to be included in the CSV.
            label_columns (dict[str, str]): The mapping of column names to labels.
            with_header (bool, optional): Whether to include the header in the CSV. Defaults to True.
            delimiter (str, optional): The delimiter to use in the CSV. Defaults to ",".
            quotechar (str | None, optional): Quote character for the CSV file. If not given, it will not be used. Defaults to None.
            relation_separator (str, optional): The separator to use for nested keys. Defaults to ".".
            export_mode (ExportMode, optional): Export mode (simplified or detailed). Defaults to "simplified".

        Returns:
            str: The CSV data as a string.
        """
        csv_data = ""
        line = Line()
        writer = csv.writer(line, delimiter=delimiter, quotechar=quotechar)

        if with_header:
            header = [label_columns[col] for col in list_columns]
            writer.writerow(header)
            csv_data = line.read()

        if isinstance(data, dict):
            data = [data]

        for item in data:
            row = cls._json_to_csv(
                item,
                list_columns=list_columns,
                delimiter=delimiter,
                relation_separator=relation_separator,
                export_mode=export_mode,
            )
            writer.writerow(row)
            csv_data += line.read()

        return csv_data.strip()

    @classmethod
    def _json_to_csv(
        self,
        data: dict[str, typing.Any],
        /,
        *,
        list_columns: list[str],
        delimiter=",",
        relation_separator=".",
        export_mode: ExportMode = "simplified",
    ):
        """
        Converts single JSON object to CSV format.

        Args:
            data (dict[str, Any]): The JSON data to be converted.
            list_columns (list[str]): The list of columns to be included in the CSV.
            delimiter (str, optional): The delimiter to use in the CSV. Defaults to ",".
            relation_separator (str, optional): The separator to use for nested keys. Defaults to ".".
            export_mode (ExportMode, optional): Export mode (simplified or detailed). Defaults to "simplified".

        Returns:
            str: The CSV data as a string.
        """
        csv_data: list[str] = []

        for col in list_columns:
            sub_col = []
            if relation_separator in col:
                col, *sub_col = col.split(relation_separator)
            curr_val = data.get(col, "")
            for sub in sub_col:
                if isinstance(curr_val, dict):
                    curr_val = curr_val.get(sub, "")
                else:
                    curr_val = ""

            if isinstance(curr_val, dict):
                curr_val = curr_val.get("name_", curr_val)
            elif isinstance(curr_val, list):
                curr_val = [
                    curr_val.get(
                        "id_" if export_mode == "detailed" else "name_",
                        json.dumps(curr_val),
                    )
                    for curr_val in curr_val
                ]
                array_separator = "," if delimiter == ";" else ";"
                curr_val = array_separator.join(curr_val)
            elif isinstance(curr_val, enum.Enum):
                curr_val = curr_val.value
            if curr_val is not None:
                if isinstance(curr_val, dict):
                    curr_val = json.dumps(curr_val)
                else:
                    curr_val = str(curr_val)
            else:
                curr_val = ""
            csv_data.append(curr_val)

        return csv_data

    @classmethod
    def _convert_nested_col_into_dict(
        cls,
        data: dict[str, typing.Any],
        /,
        *,
        separator: str = ".",
        list_delimiter: str = ";",
    ):
        """
        Converts nested columns in a dictionary into a nested dictionary.

        Args:
            data (dict[str, Any]): The dictionary to be converted.
            separator (str, optional): Separator used to split the keys into nested dictionaries. Defaults to ".".
            list_delimiter (str, optional): Delimiter used to join list values. Defaults to ";"

        Returns:
            dict[str, Any]: The converted dictionary with nested keys.

        Example:
        ```python
            data = {
                "name": "Alice",
                "age": 30,
                "address.city": "New York",
                "address.state": "NY",
            }
            result = CSVJSONConverter._convert_nested_col_into_dict(data)
            # result = {
            #     "name": "Alice",
            #     "age": 30,
            #     "address": {
            #         "city": "New York",
            #         "state": "NY"
            #     }
            # }
        ```
        """
        result: dict[str, typing.Any] = {}
        for key, value in data.items():
            parts = key.strip().split(separator)
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value

            if list_delimiter in value:
                value = value.split(list_delimiter)
                current[parts[-1]] = [item.strip() for item in value if item.strip()]
        return result

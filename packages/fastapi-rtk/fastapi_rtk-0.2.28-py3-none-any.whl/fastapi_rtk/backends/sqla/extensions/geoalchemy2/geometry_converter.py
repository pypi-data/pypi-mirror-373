import json
import typing

import geoalchemy2
import shapely

__all__ = ["GeometryConverter"]


class GeometryConverter:
    def two_way_converter_generator(self, type=""):
        """
        Generate a two-way converter for a specific geometry type.

        Args:
            type (str, optional): The geometry type. Defaults to ''.

        Returns:
            Callable[[geoalchemy2.WKBElement | shapely.geometry.base.BaseGeometry | dict[str, typing.Any] | str], typing.Any]: The two-way converter.
        """

        def two_way_converter(
            value: (
                geoalchemy2.WKBElement
                | shapely.geometry.base.BaseGeometry
                | dict[str, typing.Any]
                | str
            ),
        ):
            return self.two_way_converter(value, type)

        return two_way_converter

    def two_way_converter(
        self,
        value: (
            geoalchemy2.WKBElement
            | shapely.geometry.base.BaseGeometry
            | dict[str, typing.Any]
            | str
        ),
        type: str = "",
    ):
        """
        Convert between WKB, WKT, GeoJSON, and shapely geometries.

        - WKBElement -> GeoJSON
        - BaseGeometry -> GeoJSON
        - GeoJSON -> WKT
        - WKT -> WKT (Check validity)

        Args:
            value (geoalchemy2.WKBElement | shapely.geometry.base.BaseGeometry | dict[str, typing.Any] | str): Value to convert.
            type (str, optional): The geometry type to check for. Empty means no check. Defaults to "".

        Raises:
            ValueError: If the value is not a valid geometry.

        Returns:
            dict[str, typing.Any] | str: Converted value.
        """
        if isinstance(value, geoalchemy2.WKBElement) or isinstance(
            value, shapely.geometry.base.BaseGeometry
        ):
            return self.to_geojson(value)

        if isinstance(value, dict):
            try:
                return self.from_geojson(json.dumps(value)).wkt
            except shapely.errors.GEOSException as e:
                raise ValueError(str(e))

        try:
            value_type = shapely.from_wkt(value).geom_type.capitalize()
            type = type.capitalize()
            if type and value_type != type:
                raise ValueError(f"Expected {type} but got {value_type}")
        except shapely.errors.GEOSException as e:
            raise ValueError(str(e))
        return value

    def to_geojson(
        self, value: shapely.geometry.base.BaseGeometry | geoalchemy2.WKBElement
    ):
        """
        Convert a shapely geometry or WKBElement to GeoJSON.

        Args:
            value (shapely.geometry.base.BaseGeometry | geoalchemy2.WKBElement): Geometry to convert.

        Returns:
            dict[str, typing.Any]: Converted GeoJSON.
        """
        if isinstance(value, geoalchemy2.WKBElement):
            value = self.from_wkb(value)
        data: dict[str, typing.Any] = json.loads(shapely.to_geojson(value))
        return data

    def from_wkb(self, value: geoalchemy2.WKBElement):
        """
        Convert a WKBElement to a shapely geometry.

        Args:
            value (geoalchemy2.WKBElement): WKBElement to convert.

        Returns:
            shapely.geometry.base.BaseGeometry: Converted geometry.
        """
        return geoalchemy2.shape.to_shape(value)

    def from_geojson(self, value: dict[str, typing.Any] | str):
        """
        Convert a GeoJSON string or dict to a shapely geometry.

        Args:
            value (dict[str, typing.Any] | str): GeoJSON to convert.

        Raises:
            ValueError: If the GeoJSON is not valid.

        Returns:
            shapely.geometry.base.BaseGeometry: Converted geometry.
        """
        if isinstance(value, dict):
            value = json.dumps(value)
        return shapely.from_geojson(value, on_invalid="raise")

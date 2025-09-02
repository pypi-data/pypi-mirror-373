__all__ = [
    # .filters
    "GeoBaseFilter",
    "GeoFilterEqual",
    "GeoFilterNotEqual",
    "GeoFilterContains",
    "GeoFilterNotContains",
    "GeoFilterIntersects",
    "GeoFilterNotIntersects",
    "GeoFilterOverlaps",
    "GeoFilterNotOverlaps",
    # .geometry_converter
    "GeometryConverter",
]

try:
    import geoalchemy2
    import shapely

    from .filters import *
    from .geometry_converter import *


except ImportError:

    class _GeoAlchemy2ImportError:
        def __init__(self, name):
            self._name = name

        def __getattr__(self, attr):
            raise ImportError(
                f"geoalchemy2 and shapely are not installed, but you tried to access '{self._name}.{attr}'. "
                "Please install geoalchemy2 and shapely to use GeoAlchemy2 features."
            )

        def __call__(self, *args, **kwargs):
            raise ImportError(
                f"geoalchemy2 and shapely are not installed, but you tried to instantiate '{self._name}'. "
                "Please install geoalchemy2 and shapely to use GeoAlchemy2 features."
            )

    GeoBaseFilter = _GeoAlchemy2ImportError("GeoBaseFilter")
    GeoFilterEqual = _GeoAlchemy2ImportError("GeoFilterEqual")
    GeoFilterNotEqual = _GeoAlchemy2ImportError("GeoFilterNotEqual")
    GeoFilterContains = _GeoAlchemy2ImportError("GeoFilterContains")
    GeoFilterNotContains = _GeoAlchemy2ImportError("GeoFilterNotContains")
    GeoFilterIntersects = _GeoAlchemy2ImportError("GeoFilterIntersects")
    GeoFilterNotIntersects = _GeoAlchemy2ImportError("GeoFilterNotIntersects")
    GeoFilterOverlaps = _GeoAlchemy2ImportError("GeoFilterOverlaps")
    GeoFilterNotOverlaps = _GeoAlchemy2ImportError("GeoFilterNotOverlaps")
    GeometryConverter = _GeoAlchemy2ImportError("GeometryConverter")

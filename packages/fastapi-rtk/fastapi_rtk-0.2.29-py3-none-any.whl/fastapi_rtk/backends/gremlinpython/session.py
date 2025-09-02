from .db import graph_db

__all__ = ["get_graph_traversal_factory"]


def get_graph_traversal_factory(keep_open=False):
    """
    Factory function that returns a generator for creating Gremlin graph traversals.

    Can be used as a dependency in FastAPI routes.

    Args:
        keep_open (bool, optional): Whether to keep the connection open after use. Defaults to False.

    Returns:
        typing.Callable[[], typing.Generator[gremlin_python.process.graph_traversal.GraphTraversal, Any, None]]: A generator function that yields a graph traversal object.
    """

    def get_graph_traversal():
        with graph_db.session(keep_open=keep_open) as session:
            yield session

    return get_graph_traversal

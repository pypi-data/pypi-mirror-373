"""Cognee Community Graph Adapter - Memgraph

This package provides a Memgraph graph database adapter for the Cognee framework.
"""

from .memgraph_adapter import MemgraphAdapter

__version__ = "0.1.0"
__all__ = ["MemgraphAdapter", "register"]


def register():
    """Register the Memgraph adapter with cognee's supported databases."""
    try:
        from cognee.infrastructure.databases.graph.supported_databases import (
            supported_databases,
        )

        supported_databases["memgraph"] = MemgraphAdapter
    except ImportError:
        raise ImportError(
            "cognee is not installed. Please install it with: pip install cognee"
        )

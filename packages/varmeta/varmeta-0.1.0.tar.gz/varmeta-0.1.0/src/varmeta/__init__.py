"""varmeta: Lightweight variable metadata management for data workflows.

This package provides hashable variable objects with units, descriptions, and
component support, enabling robust metadata handling, serialization, and
integration with pandas and other tools.
"""

__version__ = "0.1.0"

from .vars import (
    Var,
    VarData,
    VarDict,
    dict_to_df,
    records_to_df,
    unpack,
    vars_from_dict,
    vars_to_dict,
    vars_to_multi_index_data,
)

__all__ = [
    "Var",
    "vars_to_multi_index_data",
    "dict_to_df",
    "VarData",
    "VarDict",
    "records_to_df",
    "unpack",
    "vars_to_dict",
    "vars_from_dict",
]

import logging
from logging import NullHandler

from .__about__ import __version__
from .es_inspector import EsMappingInspector
from .main import MappingMismatchError, compare_es_mapping_with_model
from .pydantic_inspector import get_pydantic_model_fields

logging.getLogger(__name__).addHandler(NullHandler())

__all__ = [
    "__version__",
    "compare_es_mapping_with_model",
    "MappingMismatchError",
    "EsMappingInspector",
    "get_pydantic_model_fields",
]

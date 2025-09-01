# pydantic_inspector.py
from __future__ import annotations

import logging
from enum import Enum

from pydantic import BaseModel

from .utils import is_list_type, is_union_type

logger = logging.getLogger(__name__)


def get_pydantic_model_fields(model: BaseModel, prefix: str = "") -> tuple[dict, list]:
    """
    Recursively extract a flattened view of all fields and types from a Pydantic model.

    Parameters
    ----------
    model : BaseModel
        The Pydantic model class to inspect (not an instance).
    prefix : str, optional
        Optional path prefix used during recursion.

    Returns
    -------
    tuple[dict, list]
        - fields: dict mapping `"dot.notation"` paths to either a Python type,
        or markers `list` / `dict`.
        - errors: list of strings describing ambiguous union annotations encountered.

    Notes
    -----
    - `Optional[T]` / `Union[T, None]` is unwrapped to `T`.
    - `List[SubModel]` registers the path as `list` and recurses into `SubModel`.
    - `List[Enum]` unwraps to the Enum's base (`str` or `int`) where possible.
    - Nested `BaseModel` annotations register as `dict` and recurse.
    """
    fields: dict[str, type] = {}
    errors: list[str] = []

    def _typename(tp) -> str:
        """Normalize a Python/Enum type into a string name."""
        if tp is None:
            return None
        if isinstance(tp, type):
            if issubclass(tp, Enum):
                # unwrap to underlying base type name
                if issubclass(tp, str):
                    return str
                if issubclass(tp, int):
                    return int
                return tp
            return tp
        return tp

    def _recurse(cur_model, cur_prefix: str):
        for name, field in cur_model.model_fields.items():
            full = f"{cur_prefix}.{name}" if cur_prefix else name
            ann = field.annotation

            # 1) Handle Optional / Union[..., None]
            if is_union_type(ann):
                args = getattr(ann, "__args__", ())
                # strip out NoneType
                non_none = [a for a in args if a is not type(None)]
                if len(non_none) != 1:
                    errors.append(f"Field '{full}' has ambiguous union types {tuple(args)}")
                    continue
                ann = non_none[0]

            # 2) Handle List[...]
            if is_list_type(ann):
                args = getattr(ann, "__args__", ())
                elem = args[0] if args else None

                # nested BaseModel
                if elem and hasattr(elem, "model_fields"):
                    fields[full] = list
                    _recurse(elem, full)

                # Enum subclass → unwrap to its base (str or int)
                elif isinstance(elem, type) and issubclass(elem, Enum):
                    # detect base by inheritance
                    if issubclass(elem, str):
                        fields[full] = str
                    elif issubclass(elem, int):
                        fields[full] = int
                    else:
                        # fallback to enum class itself
                        fields[full] = elem

                # primitive or other non‐model
                elif elem:
                    fields[full] = elem

                # unknown list contents
                else:
                    fields[full] = list

            # 3) Handle nested BaseModel
            elif hasattr(ann, "model_fields"):
                fields[full] = dict
                _recurse(ann, full)

            # 4) Primitive or other
            else:
                fields[full] = _typename(ann)

    _recurse(model, prefix)

    return fields, errors

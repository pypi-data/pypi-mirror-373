# utils.py
import types


def is_union_type(tp):
    """
    Return whether the annotation represents a `Union` (incl. `X | Y` syntax).

    Parameters
    ----------
    tp :
        A type annotation object.

    Returns
    -------
    bool
        True if `tp` is a union type; otherwise False.
    """
    return isinstance(tp, types.UnionType)


def is_list_type(tp):
    """
    Return whether the annotation represents a parametrized `list[...]`.

    Parameters
    ----------
    tp :
        A type annotation object.

    Returns
    -------
    bool
        True if `tp` is a `list` generic alias (e.g., `list[int]`); otherwise False.
    """
    return isinstance(tp, types.GenericAlias) and tp.__origin__ is list

"""Visualize huge Python objects as nicely reduced strings."""

from pprint import pformat
from typing import Any


class Dots(dict):  # type: ignore # inherit from dict to blend with expected type
    """Show dots inside Python objects repr."""

    def __repr__(self) -> str:
        """Show dots."""
        return ".."


def ellipsize(  # noqa: PLR0911
    obj: Any,
    max_items_to_show: int = 10,
    max_item_length: int = 1024,
) -> Any:
    """Reduce huge list/dict to show on screen.

    In lists (including dict items) show only 1st `max_list_items_to_show`
    and add ".." if there is more.
    Limit max dict/list length at max_item_length.

    Args:
        obj: Python object to ellipsize
        max_items_to_show: if List or Dict in obj (including nested) has more items,
            then show ".." instead of the rest items
        max_item_length: if List's or Dict's item are not another List/Dict
            and his string representation longer than show ".." instead of the rest of it
    """
    if isinstance(obj, (int, float)):
        return obj
    if isinstance(obj, list):
        if len(obj) == 0:
            return obj
        return ellipsize_list(obj, max_items_to_show, max_item_length)
    if isinstance(obj, tuple):
        if len(obj) == 0:
            return obj
        return tuple(ellipsize_list(list(obj), max_items_to_show, max_item_length))
    if isinstance(obj, dict):
        if len(obj) == 0:
            return obj
        return ellipsize_dict(obj, max_items_to_show, max_item_length)
    suffix = ".." if len(str(obj)) > max_item_length else ""
    return str(obj)[:max_item_length] + suffix


def ellipsize_list(
    obj: list[Any],
    max_items_to_show: int,
    max_item_length: int,
) -> list[Any]:
    """Ellipsize list."""
    result_list = [
        ellipsize(
            val,
            max_items_to_show=max_items_to_show,
            max_item_length=max_item_length,
        )
        for val in obj[:max_items_to_show]
    ]
    if len(obj) > max_items_to_show:
        result_list.append(Dots())
    return result_list


def ellipsize_dict(
    obj: dict[Any, Any],
    max_items_to_show: int,
    max_item_length: int,
) -> dict[Any, Any]:
    """Ellipsize dict."""
    items = list(obj.items())[:max_items_to_show]
    result_dict: dict[Any, Any] = {
        key: ellipsize(
            val,
            max_items_to_show=max_items_to_show,
            max_item_length=max_item_length,
        )
        for key, val in items
    }
    if len(obj) > max_items_to_show:
        result_dict[".."] = Dots()
    return result_dict


def format_ellipsized(
    obj: Any,
    max_items_to_show: int = 10,
    max_item_length: int = 1024,
) -> str:
    """Pformat ellipsized `obj`.

    Use [pprint.pformat](https://docs.python.org/3/library/pprint.html)
    to convert ellipsize result into string

    Args:
        obj: Python object to ellipsize
        max_items_to_show: if List or Dict in obj (including nested) has more items,
            then show ".." instead of the rest items
        max_item_length: if List's or Dict's item are not another List/Dict
            and his string representation longer than show ".." instead of the rest of it
    """
    return pformat(
        ellipsize(
            obj,
            max_items_to_show=max_items_to_show,
            max_item_length=max_item_length,
        ),
    )


def print_ellipsized(
    *objs: Any,
    max_items_to_show: int = 10,
    max_item_length: int = 1024,
    **kwargs: Any,
) -> None:
    """Print ellipsized `obj` with [pprint](https://docs.python.org/3/library/pprint.html).

    Can print many objects, like general print.
    Pass args to print like [end](https://realpython.com/lessons/sep-end-and-flush/).

    Args:
        objs: Python objects to ellipsize
        max_items_to_show: if List or Dict in objs (including nested) has more items,
            then show ".." instead of the rest items
        max_item_length: if List's or Dict's item are not another List/Dict
            and his string representation longer than show ".." instead of the rest of it
    """
    print(
        *[
            pformat(
                ellipsize(
                    obj,
                    max_items_to_show=max_items_to_show,
                    max_item_length=max_item_length,
                ),
            )
            for obj in objs
        ],
        **kwargs,
    )

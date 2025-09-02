"""Mimicking the functional programming tools from R and the R package purrr."""

from itertools import repeat
from typing import Callable, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def _map(x: list[T], fn: Callable[[T], U]) -> list[U]:
    """Use a function on each item in a list.

    This is a simpler, more user-friendly version of the built-in `map()`
    function. This function takes a list and a function, applies the function
    to each item in the list, and returns a new list with the results.
    This is mostly a thin wrapper around the built-in `map()` function.

    Inspired from the functionals from the R package purrr.

    Args:
        x: A list object.
        fn: A function to use on each item in the list `x`.

    Returns:
        A list with the results of applying `fn` to each item in `x`.
        The length of the list is the same as `x`.

    Examples:
        ```{python}
        from seedcase_sprout.internals import _map
        def square(x):
            return x * x
        _map([1, 2, 3], square)
        ```
    """
    return list(map(fn, x))


def _map2(x: list[T], y: list[U], fn: Callable[[T, U], V]) -> list[V]:
    """Use a function on each item in two lists, placed on the first two arguments.

    This function is similar to the `map2()` function from the R package purrr.
    It takes two lists and a function as arguments. The function is applied to
    each pair of elements from the two lists. If the second list has only one
    element, it is repeated for each element in the first list. The output
    is the same size as the first list.

    This makes the function a bit more user-friendly compared to the built-in
    `map()` function, which requires the same length for both lists.

    Args:
        x: The first list to use the function on.
        y: The second list that must have the same items as the first `x` list or one
            item to be repeated.
        fn: The function to use on each pair of items in the two lists above.

    Returns:
        A list of the results from the function used on each item in the two lists.

    Examples:
        ```{python}
        from seedcase_sprout.internals import _map2
        def add(a, b):
            return a + b
        _map2(
            x=[1, 2, 3],
            y=[10],
            fn=add
        )

        _map2(
            x=[1, 2, 3],
            y=[10, 20, 30],
            fn=add
        )
        ```
    """
    if len(y) == 1:
        y = list(repeat(y[0], len(x)))
    return list(map(fn, x, y))

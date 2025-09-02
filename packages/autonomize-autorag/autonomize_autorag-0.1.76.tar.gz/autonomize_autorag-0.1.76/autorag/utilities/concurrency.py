"""Module that handles concurrency in a synchronous task."""

import functools
from typing import Callable, ParamSpec, TypeVar

import anyio.to_thread

P = ParamSpec("P")
T = TypeVar("T")


async def run_async(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """
    Asynchronously runs a synchronous function.

    This function allows you to execute a blocking or synchronous function in an asynchronous
    context by offloading the execution to a separate thread.

    Type Variables:
        P (ParamSpec): A special kind of type variable used to represent the parameter types
                       of the callable. It captures the parameter specification (types of
                       arguments) of the function.
        T (TypeVar): A regular type variable representing the return type of the callable.

    Args:
        func (Callable[P, T]): The synchronous function to be executed.
        *args: Positional arguments to be passed to the function.
        **kwargs: Keyword arguments to be passed to the function.

    Returns:
        T: The result of the function execution.
    """
    if kwargs:  # pragma: no cover
        # run_sync doesn't work with kwargs,
        # so using this workaround to bind them to the function
        func = functools.partial(func, **kwargs)
    return await anyio.to_thread.run_sync(func, *args)

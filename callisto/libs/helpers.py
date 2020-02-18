from __future__ import annotations

import functools
import typing as t


T = t.TypeVar('T')


def async_partial(func: t.Callable[..., t.Awaitable[T]],
                  *args: t.Any,
                  **kwargs: t.Any) -> t.Callable[..., t.Awaitable[T]]:
    """We need this, because functools.partial loses the coroutine marker
    (for introspection it's just a regular function).

    Our wrapper here is async function itself, so introspection works fine.
    """

    async def wrapper(*args_: t.Any, **kwargs_: t.Any) -> T:
        kwargs_copy = kwargs.copy()
        kwargs_copy.update(kwargs_)

        return await functools.partial(func, *(args + args_), **kwargs_copy)()

    return functools.update_wrapper(wrapper, func)

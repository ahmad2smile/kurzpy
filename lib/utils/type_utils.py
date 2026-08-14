import functools
import inspect
from collections.abc import Callable
from typing import Any


def replace_param_type(method: Callable[..., Any], **overrides: type[Any]) -> Callable[..., Any]:  # pyright: ignore[reportExplicitAny]
    """Replaces specific param of a method with the ones in overrides"""

    @functools.wraps(method)
    async def endpoint(*args, **kwargs):
        return await method(*args, **kwargs)

    sig = inspect.signature(method)
    params = [p.replace(annotation=overrides[p.name]) if p.name in overrides else p for p in sig.parameters.values()]

    # Endpoint becomes the method with "corrected" parameter type, Required by FastApi doc setup
    endpoint.__signature__ = sig.replace(parameters=params)  # type: ignore[valid-type]

    return endpoint

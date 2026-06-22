import functools
import inspect


def replace_param_type(method, **overrides):
    """Replaces specific param of a method with the ones in overrides"""

    @functools.wraps(method)
    async def endpoint(*args, **kwargs):
        return await method(*args, **kwargs)

    sig = inspect.signature(method)
    params = [
        p.replace(annotation=overrides[p.name]) if p.name in overrides else p
        for p in sig.parameters.values()
    ]

    endpoint.__signature__ = sig.replace(parameters=params)  # type: ignore[valid-type]
    return endpoint

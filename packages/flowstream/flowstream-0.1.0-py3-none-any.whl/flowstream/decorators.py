from typing import Callable, Awaitable, Any
from fastapi import Request
from .app import StreamApp
import inspect

def stream(path: str):
    def deco(func):
        func._flowstream_path = path
        sig = inspect.signature(func)
        param_names = [p.name for p in sig.parameters.values()]

        def wrapper(request: Request, **path_params):
            # 若函式第一參數是 request/req，就帶 request；否則不要帶
            kwargs = dict(path_params)
            if param_names and param_names[0] in ("request", "req"):
                return func(request, **kwargs)
            return func(**kwargs)

        wrapper._flowstream_path = path
        wrapper._flowstream_original = func
        return wrapper
    return deco

def register_streams(app: StreamApp, *handlers):
    for h in handlers:
        p = getattr(h, "_flowstream_path", None)
        if not p:
            raise ValueError("Use @stream(path='...') on your handler.")
        app.mount_stream_route(p, h)

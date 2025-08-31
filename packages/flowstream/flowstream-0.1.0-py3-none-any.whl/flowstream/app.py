from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from .sse import sse_stream
import inspect

class StreamApp(FastAPI):
    def mount_stream_route(self, path: str, handler, *, media_type="text/event-stream"):
        async def endpoint(request: Request):
            path_params = request.path_params or {}
            # 先嘗試帶 request + path 參數呼叫
            try_call = handler
            try:
                gen_or_coro = try_call(request, **path_params)
            except TypeError:
                # 如果 handler 不吃 request，就只傳 path 參數
                gen_or_coro = try_call(**path_params)

            # 如果回傳的是 coroutine，要先 await 拿到 async generator
            if inspect.iscoroutine(gen_or_coro):
                gen = await gen_or_coro
            else:
                gen = gen_or_coro

            return StreamingResponse(
                sse_stream(gen),
                media_type=media_type,
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        self.add_api_route(path, endpoint, methods=["GET"])



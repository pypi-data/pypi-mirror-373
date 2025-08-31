from typing import AsyncIterator
from fastapi import Request
from flowstream import StreamApp, stream, register_streams
import anyio

app = StreamApp(title="Flowstream Example")

@stream("/chat")
async def chat(request: Request) -> AsyncIterator[str]:
    q = request.query_params.get("q", "Hello")
    text = f"你說：{q} —— 這是流式打字示範。"
    for ch in text:
        yield ch                 # 關鍵：真的逐字送
        await anyio.sleep(0.05)  # 放慢，確保觀察得到

#@stream("/chat")
#async def chat():
#    for ch in "Hello":
#        yield ch
#        await anyio.sleep(0.05)
register_streams(app, chat)


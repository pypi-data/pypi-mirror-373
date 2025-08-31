# sse.py — hardened SSE stream (貼上覆蓋)
from typing import AsyncIterator, Iterable, Union, AsyncGenerator
import anyio, time
from anyio import get_cancelled_exc_class

SSE_END_EVENT = "event: end\ndata: [END]\n\n"
SSE_HEARTBEAT = ": keep-alive\n\n"  # 註解行，不會觸發 onmessage

def _fmt(data: str) -> bytes:
    # 多行都要 data: 前綴，最後多一個空行分隔事件
    body = "".join(f"data: {line}\n" for line in data.splitlines()) + "\n"
    return body.encode("utf-8")

async def _aiter(gen: Union[AsyncIterator[str], AsyncGenerator[str, None], Iterable[str]]):
    if hasattr(gen, "__anext__"):
        async for item in gen:
            yield item
    else:
        for item in gen:
            yield item

async def sse_stream(
    gen: Union[AsyncIterator[str], AsyncGenerator[str, None], Iterable[str]],
    heartbeat_interval: float = 15.0,
) -> AsyncIterator[bytes]:
    """
    將字串/token 串流包成正確 SSE，並：
    - 一開始先送一個 keep-alive，避免某些客戶端/代理誤判。
    - 空閒時定期送心跳。
    - 無論正常或被取消/錯誤，盡力送出結尾事件讓客戶端優雅結束。
    """
    cancelled_exc = get_cancelled_exc_class()
    last_send = time.monotonic()

    # 起手吐一個心跳，讓連線立即有資料（避免某些工具誤判）
    yield SSE_HEARTBEAT.encode("utf-8")

    try:
        async for chunk in _aiter(gen):
            yield _fmt(str(chunk))
            last_send = time.monotonic()
            # 讓步，避免壓爆事件迴圈
            await anyio.sleep(0)
            # 太久沒資料 → 送心跳
            if time.monotonic() - last_send > heartbeat_interval:
                yield SSE_HEARTBEAT.encode("utf-8")
                last_send = time.monotonic()
    except cancelled_exc:
        # 客戶端主動關閉（重整/離開），不視為錯誤
        pass
    except Exception:
        # 出錯也嘗試送結尾，避免客戶端掛著等
        try:
            yield SSE_END_EVENT.encode("utf-8")
        finally:
            raise
    else:
        # 正常完成 → 送結尾事件
        yield SSE_END_EVENT.encode("utf-8")

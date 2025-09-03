import os
import asyncio
import threading
import time
from pydantic import PrivateAttr
from langchain_gigachat.chat_models import GigaChat
from langchain_gigachat import GigaChatEmbeddings
import langchain_gigachat.embeddings.gigachat

langchain_gigachat.embeddings.gigachat.MAX_BATCH_SIZE_PARTS=int(os.getenv("EMBEDDINGS_MAX_BATCH_SIZE_PARTS", "90"))

MAX_CHAT_CONCURRENCY = int(os.getenv("MAX_CHAT_CONCURRENCY", "100000"))
MAX_EMBED_CONCURRENCY = int(os.getenv("MAX_EMBED_CONCURRENCY", "100000"))


from agent_lab_sdk.metrics import get_metric
from agent_lab_sdk.llm.gigachat_token_manager import GigaChatTokenManager

def create_metrics(prefix: str):
    in_use = get_metric(
        metric_type = "gauge", name = f"{prefix}_slots_in_use",
        documentation = f"Number of {prefix} slots currently in use"
    )
    waiting = get_metric(
        metric_type = "gauge", name = f"{prefix}_waiting_tasks",
        documentation = f"Number of tasks waiting for {prefix}"
    )
    wait_time = get_metric(
        metric_type = "histogram", name = f"{prefix}_wait_time_seconds",
        documentation = f"Time tasks wait for {prefix}",
        buckets = [3, 5, 10, 15, 30, 60, 120, 240, 480, 960, 1920, float("inf")]
    )

    return in_use, waiting, wait_time

chat_in_use, chat_waiting, chat_wait_hist = create_metrics("chat")
embed_in_use, embed_waiting, embed_wait_hist = create_metrics("embed")

class UnifiedSemaphore:
    """Threading-based семафор + sync/async API + metrics + контекстники."""
    def __init__(self, limit, in_use, waiting, wait_hist):
        self._sem       = threading.Semaphore(limit)
        self._limit     = limit
        self._in_use    = in_use
        self._waiting   = waiting
        self._wait_hist = wait_hist
        self._current   = 0

        self._in_use.set(0)
        self._waiting.set(0)

    # ——— синхронный API ———
    def acquire(self):
        self._waiting.inc()
        start = time.time()

        self._sem.acquire()
        elapsed = time.time() - start
        self._wait_hist.observe(elapsed)
        self._waiting.dec()

        self._current += 1
        self._in_use.set(self._current)

    def release(self):
        self._sem.release()
        self._current -= 1
        self._in_use.set(self._current)

    # контекстник для sync
    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()

    # ——— асинхронный API ———
    async def acquire_async(self):
        self._waiting.inc()
        start = time.time()
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._sem.acquire)
        elapsed = time.time() - start
        self._wait_hist.observe(elapsed)
        self._waiting.dec()

        self._current += 1
        self._in_use.set(self._current)

    async def release_async(self):
        # release очень быстрый
        self._sem.release()
        self._current -= 1
        self._in_use.set(self._current)

    # контекстник для async
    async def __aenter__(self):
        await self.acquire_async()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.release_async()

# Semaphores for chat and embeddings
_semaphores = {
    "chat": UnifiedSemaphore(MAX_CHAT_CONCURRENCY, chat_in_use, chat_waiting, chat_wait_hist),
    "embed": UnifiedSemaphore(MAX_EMBED_CONCURRENCY, embed_in_use, embed_waiting, embed_wait_hist),
}

class ThrottledGigaChatEmbeddings(GigaChatEmbeddings):
    _manage_access_token: bool = PrivateAttr(default=True)
    _base_kwargs: dict = PrivateAttr(default={})

    def __init__(self, *args, manage_access_token=True, **kwargs):
        print(self)
        self._manage_access_token = manage_access_token
        self._base_kwargs = dict(kwargs)

        if self._manage_access_token and "access_token" not in kwargs:
            token = GigaChatTokenManager.get_token()
            super().__init__(access_token=token, **kwargs)
        else:
            super().__init__(**kwargs)

    def _fresh(self) -> GigaChatEmbeddings:
        if self._manage_access_token:
            return GigaChatEmbeddings(access_token=GigaChatTokenManager.get_token(), **self._base_kwargs)
        else:    
            return self


    def embed_documents(self, *args, **kwargs):
        with _semaphores["embed"]:
            return self._fresh().embed_documents(*args, **kwargs)

    def embed_query(self, *args, **kwargs):
        with _semaphores["embed"]:
            return self._fresh().embed_query(*args, **kwargs)

    async def aembed_documents(self, *args, **kwargs):
        async with _semaphores["embed"]:
            return await self._fresh().aembed_documents(*args, **kwargs)

    async def aembed_query(self, *args, **kwargs):
        async with _semaphores["embed"]:
            return await self._fresh().aembed_query(*args, **kwargs)

class ThrottledGigaChat(GigaChat):
    _manage_access_token: bool = PrivateAttr(default=True)
    _base_kwargs: dict = PrivateAttr(default={})

    def __init__(self, *args, manage_access_token=True, **kwargs):
        print(self)
        self._manage_access_token = manage_access_token
        self._base_kwargs = dict(kwargs)

        if self._manage_access_token and "access_token" not in kwargs:
            token = GigaChatTokenManager.get_token()
            super().__init__(access_token=token, **kwargs)
        else:
            super().__init__(**kwargs)

    def _fresh(self) -> GigaChat:
        if self._manage_access_token:
            return GigaChat(access_token=GigaChatTokenManager.get_token(), **self._base_kwargs)
        else:    
            return self

    def invoke(self, *args, **kwargs):
        with _semaphores["chat"]:
            return self._fresh().invoke(*args, **kwargs)

    async def ainvoke(self, *args, **kwargs):
        async with _semaphores["chat"]:
            return await self._fresh().ainvoke(*args, **kwargs)

    def stream(self, *args, **kwargs):
        with _semaphores["chat"]:
            for chunk in self._fresh().stream(*args, **kwargs):
                yield chunk

    async def astream(self, *args, **kwargs):
        async with _semaphores["chat"]:
            async for chunk in self._fresh().astream(*args, **kwargs):
                yield chunk

    async def astream_events(self, *args, **kwargs):
        async with _semaphores["chat"]:
            async for ev in self._fresh().astream_events(*args, **kwargs):
                yield ev

    def batch(self, *args, **kwargs):
        with _semaphores["chat"]:
            return self._fresh().batch(*args, **kwargs)

    async def abatch(self, *args, **kwargs):
        async with _semaphores["chat"]:
            return await self._fresh().abatch(*args, **kwargs)
        
    def upload_file(self, *args, **kwargs):
        with _semaphores["chat"]:
            return self._fresh().upload_file(*args, **kwargs)

    async def aupload_file(self, *args, **kwargs):
        async with _semaphores["chat"]:
            return await self._fresh().aupload_file(*args, **kwargs)

    def batch_as_completed(self, *args, **kwargs):
        with _semaphores["chat"]:
            for item in self._fresh().batch_as_completed(*args, **kwargs):
                yield item

    async def abatch_as_completed(self, *args, **kwargs):
        async with _semaphores["chat"]:
            async for item in self._fresh().abatch_as_completed(*args, **kwargs):
                yield item

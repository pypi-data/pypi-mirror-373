from __future__ import annotations

import orjson
from random import random
from langgraph.checkpoint.serde.types import ChannelProtocol
import asyncio
import base64
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Sequence, Tuple
import logging

import httpx
from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.base import (
    WRITES_IDX_MAP,
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
    get_checkpoint_metadata,
)
from langgraph.checkpoint.serde.base import SerializerProtocol

__all__ = ["AsyncAGWCheckpointSaver"]

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# helpers for Py < 3.10
# ------------------------------------------------------------------ #
try:
    anext  # type: ignore[name-defined]
except NameError:  # pragma: no cover

    async def anext(it):
        return await it.__anext__()


class AsyncAGWCheckpointSaver(BaseCheckpointSaver):
    """Persist checkpoints in Agent-Gateway с помощью `httpx` async client."""

    # ---------------------------- init / ctx -------------------------
    def __init__(
        self,
        base_url: str = "http://localhost",
        *,
        serde: SerializerProtocol | None = None,
        timeout: int | float = 10,
        api_key: str | None = None,
        extra_headers: Dict[str, str] | None = None,
        verify: bool = True,
    ):
        super().__init__(serde=serde)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.loop = asyncio.get_running_loop()

        self.headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra_headers:
            self.headers.update(extra_headers)
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
            
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            verify=verify,
            trust_env=True
        )

    async def __aenter__(self):  # noqa: D401
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401
        await self._client.aclose()

    # ----------------------- universal dump/load ---------------------
    # def _safe_dump(self, obj: Any) -> Any:
    #     """self.serde.dump → гарантированная JSON-строка."""
    #     dumped = self.serde.dumps(obj)
    #     if isinstance(dumped, (bytes, bytearray)):
    #         return base64.b64encode(dumped).decode()  # str
    #     return dumped  # уже json-совместимо

    def _safe_dump(self, obj: Any) -> Any:
        """bytes → python-object; fallback base64 для реально бинарных данных."""
        dumped = self.serde.dumps(obj)
        if isinstance(dumped, (bytes, bytearray)):
            try:
                # 1) bytes → str
                s = dumped.decode()
                # 2) str JSON → python (list/dict/scalar)
                return orjson.loads(s)
            except (UnicodeDecodeError, orjson.JSONDecodeError):
                # не UTF-8 или не JSON → base64
                return base64.b64encode(dumped).decode()
        return dumped

    def _safe_load(self, obj: Any) -> Any:
        if isinstance(obj, (dict, list)):          # уже распакованный JSON
            return self.serde.loads(orjson.dumps(obj))
        if isinstance(obj, str):
            # сначала plain JSON-строка
            try:
                return self.serde.loads(obj.encode())
            except Exception:
                # возможно base64
                try:
                    return self.serde.loads(base64.b64decode(obj))
                except Exception:
                    return obj
        try:
            return self.serde.loads(obj)
        except Exception:
            return obj

    # def _safe_load(self, obj: Any) -> Any:
    #     """Обратная операция к _safe_dump."""
    #     if isinstance(obj, str):
    #         try:
    #             return self.serde.load(base64.b64decode(obj))
    #         except Exception:
    #             # не base64 — обычная строка
    #             return self.serde.load(obj)
    #     return self.serde.load(obj)

    # ----------------------- config <-> api --------------------------
    def _to_api_config(self, cfg: RunnableConfig | None) -> Dict[str, Any]:
        if not cfg:
            return {}
        c = cfg.get("configurable", {})
        res: Dict[str, Any] = {
            "threadId": c.get("thread_id", ""),
            "checkpointNs": c.get("checkpoint_ns", ""),
        }
        if cid := c.get("checkpoint_id"):
            res["checkpointId"] = cid
        if ts := c.get("thread_ts"):
            res["threadTs"] = ts
        return res

    # --------------------- checkpoint (de)ser ------------------------
    def _encode_cp(self, cp: Checkpoint) -> Dict[str, Any]:
        return {
            "v": cp["v"],
            "id": cp["id"],
            "ts": cp["ts"],
            "channelValues": {k: self._safe_dump(v) for k, v in cp["channel_values"].items()},
            "channelVersions": cp["channel_versions"],
            "versionsSeen": cp["versions_seen"],
            "pendingSends": cp.get("pending_sends", []),
        }

    def _decode_cp(self, raw: Dict[str, Any]) -> Checkpoint:
        return Checkpoint(
            v=raw["v"],
            id=raw["id"],
            ts=raw["ts"],
            channel_values={k: self._safe_load(v) for k, v in raw["channelValues"].items()},
            channel_versions=raw["channelVersions"],
            versions_seen=raw["versionsSeen"],
            pending_sends=raw.get("pendingSends", []),
        )

    def _decode_config(self, raw: Dict[str, Any]) -> Optional[RunnableConfig]:
        if not raw:
            return None
        return RunnableConfig(
            tags=raw.get("tags"),
            metadata=raw.get("metadata"),
            callbacks=raw.get("callbacks"),
            run_name=raw.get("run_name"),
            max_concurrency=raw.get("max_concurrency"),
            recursion_limit=raw.get("recursion_limit"),
            configurable=self._decode_configurable(raw.get("configurable"))
        )

    def _decode_configurable(self, raw: Dict[str, Any]) -> dict[str, Any]:
        return {
            "thread_id": raw.get("threadId"),
            "thread_ts": raw.get("threadTs"),
            "checkpoint_ns": raw.get("checkpointNs"),
            "checkpoint_id": raw.get("checkpointId")
        }

    # metadata (de)ser
    def _enc_meta(self, md: CheckpointMetadata) -> CheckpointMetadata:
        out: CheckpointMetadata = {}
        for k, v in md.items():
            out[k] = self._enc_meta(v) if isinstance(v, dict) else self._safe_dump(v)  # type: ignore[assignment]
        return out

    def _dec_meta(self, md: Any) -> Any:
        if isinstance(md, dict):
            return {k: self._dec_meta(v) for k, v in md.items()}
        return self._safe_load(md)

    # ------------------------ HTTP wrapper ---------------------------
    async def _http(self, method: str, path: str, **kw) -> httpx.Response:
        if "json" in kw:
            payload = kw.pop("json")
            kw["data"] = orjson.dumps(payload)
            logger.info(kw["data"].decode())
            
        return await self._client.request(method, path, **kw)

    # -------------------- api -> CheckpointTuple ----------------------
    def _to_tuple(self, node: Dict[str, Any]) -> CheckpointTuple:
        pending = None
        if node.get("pendingWrites"):
            pending = [(w["first"], w["second"], self._safe_load(w["third"])) for w in node["pendingWrites"]]
        return CheckpointTuple(
            config=self._decode_config(node["config"]),
            checkpoint=self._decode_cp(node["checkpoint"]),
            metadata=self._dec_meta(node["metadata"]),
            parent_config=self._decode_config(node.get("parentConfig")),
            pending_writes=pending,
        )

    # =================================================================
    # async-методы BaseCheckpointSaver
    # =================================================================
    async def aget_tuple(self, cfg: RunnableConfig) -> CheckpointTuple | None:
        cid = get_checkpoint_id(cfg)
        api_cfg = self._to_api_config(cfg)
        tid = api_cfg["threadId"]

        if cid:
            path = f"/checkpoint/{tid}/{cid}"
            params = {"checkpointNs": api_cfg.get("checkpointNs", "")}
        else:
            path = f"/checkpoint/{tid}"
            params = None

        resp = await self._http("GET", path, params=params)
        logger.debug("AGW aget_tuple response: %s", resp.text)

        if not resp.text:
            return None
        if resp.status_code in (404, 406):
            return None
        resp.raise_for_status()
        return self._to_tuple(resp.json())

    async def alist(
        self,
        cfg: RunnableConfig | None,
        *,
        filter: Dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        payload = {
            "config": self._to_api_config(cfg) if cfg else None,
            "filter": filter,
            "before": self._to_api_config(before) if before else None,
            "limit": limit,
        }
        resp = await self._http("POST", "/checkpoint/list", json=payload)
        logger.debug("AGW alist response: %s", resp.text)
        resp.raise_for_status()
        for item in resp.json():
            yield self._to_tuple(item)

    async def aput(
        self,
        cfg: RunnableConfig,
        cp: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        payload = {
            "config": self._to_api_config(cfg),
            "checkpoint": self._encode_cp(cp),
            "metadata": self._enc_meta(get_checkpoint_metadata(cfg, metadata)),
            "newVersions": new_versions,
        }
        resp = await self._http("POST", "/checkpoint", json=payload)
        logger.debug("AGW aput response: %s", resp.text)
        resp.raise_for_status()
        return resp.json()["config"]

    async def aput_writes(
        self,
        cfg: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        enc = [{"first": ch, "second": self._safe_dump(v)} for ch, v in writes]
        payload = {
            "config": self._to_api_config(cfg),
            "writes": enc,
            "taskId": task_id,
            "taskPath": task_path,
        }
        resp = await self._http("POST", "/checkpoint/writes", json=payload)
        logger.debug("AGW aput_writes response: %s", resp.text)
        resp.raise_for_status()

    async def adelete_thread(self, thread_id: str) -> None:
        resp = await self._http("DELETE", f"/checkpoint/{thread_id}")
        resp.raise_for_status()

    # =================================================================
    # sync-обёртки
    # =================================================================
    def _run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()

    def list(
        self,
        cfg: RunnableConfig | None,
        *,
        filter: Dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        aiter_ = self.alist(cfg, filter=filter, before=before, limit=limit)
        while True:
            try:
                yield self._run(anext(aiter_))
            except StopAsyncIteration:
                break

    def get_tuple(self, cfg: RunnableConfig) -> CheckpointTuple | None:
        return self._run(self.aget_tuple(cfg))

    def put(
        self,
        cfg: RunnableConfig,
        cp: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        return self._run(self.aput(cfg, cp, metadata, new_versions))

    def put_writes(
        self,
        cfg: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        self._run(self.aput_writes(cfg, writes, task_id, task_path))

    def delete_thread(self, thread_id: str) -> None:
        self._run(self.adelete_thread(thread_id))

    def get_next_version(self, current: Optional[str], channel: ChannelProtocol) -> str:
        if current is None:
            current_v = 0
        elif isinstance(current, int):
            current_v = current
        else:
            current_v = int(current.split(".")[0])
        next_v = current_v + 1
        next_h = random()
        return f"{next_v:032}.{next_h:016}"

    # ------------------------------------------------------------------ #
    # Convenience factory                                                #
    # ------------------------------------------------------------------ #
    @classmethod
    @asynccontextmanager
    async def from_base_url(
        cls,
        base_url: str,
        *,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator["AsyncAGWCheckpointSaver"]:
        saver = cls(base_url, api_key=api_key, **kwargs)
        try:
            yield saver
        finally:
            await saver._client.aclose()

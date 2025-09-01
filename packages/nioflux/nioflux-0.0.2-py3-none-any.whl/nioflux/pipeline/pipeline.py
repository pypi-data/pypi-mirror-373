import asyncio
import logging

from typing_extensions import Any

from nioflux.pipeline.stage import PipelineStage

logger = logging.getLogger('nioflux.pipeline')


class Pipeline:
    def __init__(self, queue: list[PipelineStage], data: Any, extra: Any,
                 io_ctx: tuple[asyncio.StreamReader, asyncio.StreamWriter] | None):
        self._queue = queue.copy()
        self._data = data
        self._extra = extra
        self._err = []
        self._fire = True
        self._io_ctx = io_ctx

    @property
    def io_ctx(self) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        return self._io_ctx

    async def launch(self) -> tuple[Any, Any, list[Exception]]:
        if not isinstance(self._queue, list):
            return self._data, self._extra, self._err
        if len(self._queue) > 0:
            for i, stage in enumerate(self._queue):
                logger.debug(f'Staging ({i + 1}/{len(self._queue)}) {stage.label}')
                self._data, self._extra, self._err, self._fire = await stage(data=self._data, extra=self._extra,
                                                                             err=self._err, fire=self._fire,
                                                                             io_ctx=self._io_ctx)
                if not self._fire:
                    break
        return self._data, self._extra, self._err

    async def __call__(self) -> tuple[Any, Any, list[Exception]]:
        return await self.launch()

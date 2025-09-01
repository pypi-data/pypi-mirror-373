import asyncio
import time
from abc import abstractmethod
from typing_extensions import Any

from vortezwohl.crypt import sha512


class PipelineStage:
    def __init__(self, label: str | None = None):
        if label is None:
            label = sha512(str(time.perf_counter()))[:16]
        self._label: str = label

    @property
    def label(self) -> str:
        return self._label

    @abstractmethod
    async def __call__(self, data: Any, extra: Any, err: list[Exception], fire: bool,
                       io_ctx: tuple[asyncio.StreamReader, asyncio.StreamWriter] | None) -> tuple[Any, Any, list[Exception], bool]:
        # data, extra, err, fire
        ...

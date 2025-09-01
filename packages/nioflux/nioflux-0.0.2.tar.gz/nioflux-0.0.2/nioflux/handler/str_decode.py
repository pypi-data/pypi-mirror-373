import asyncio
from typing_extensions import Any
from typing_extensions import override

from nioflux.pipeline.stage import PipelineStage


class StrDecode(PipelineStage):
    def __init__(self):
        super().__init__(label='str_decode')

    @override
    async def __call__(self, data: Any, extra: Any, err: list[Exception], fire: bool,
                       io_ctx: tuple[asyncio.StreamReader, asyncio.StreamWriter] | None) -> tuple[Any, Any, list[Exception], bool]:
        if isinstance(data, bytes):
            return data.decode('utf-8'), extra, err, fire
        else:
            return data, extra, err, fire

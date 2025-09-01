import asyncio
import logging
from typing_extensions import Any
from typing_extensions import override

from nioflux.pipeline.stage import PipelineStage

logger = logging.getLogger('nioflux.server')


class ErrorNotify(PipelineStage):
    def __init__(self):
        super().__init__(label='error_notify')

    @override
    async def __call__(self, data: Any, extra: Any, err: list[Exception], fire: bool,
                       io_ctx: tuple[asyncio.StreamReader, asyncio.StreamWriter] | None) -> tuple[Any, Any, list[Exception], bool]:
        _, writer = io_ctx
        _peer_host, _peer_port = writer.get_extra_info('peername')
        if len(err) > 0:
            err_log = f'Error occurred on channel {_peer_host}:{_peer_port}'
            for e in err:
                err_log += f'\n- {type(e).__name__}: {e}'
            logger.error(err_log)
        return data, extra, err, fire

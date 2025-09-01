# *NioFlux*

*A lightweight asynchronous scalable TCP frame protocol server.*

## Installation

```
pip install -U nioflux
```

or

```
uv add -U nioflux
```

## Develop you tcp frame protocol server

```python
import asyncio

from nioflux import Server, StrDecode, StrEncode, PipelineStage


class MyProtocolHandler(PipelineStage):
    def __init__(self):
        super().__init__()

    async def __call__(self, data, extra, err, fire, io_ctx):
        print('Recv:', data)
        return data, extra, err, fire


async def main():
    server = Server([StrDecode(), MyProtocolHandler(), StrEncode()])
    print('Server: ', server)
    await server.run()


if __name__ == '__main__':
    asyncio.run(main())
```

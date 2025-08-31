[![Build, test and publish](https://github.com/happydev-ca/spypoint-api/actions/workflows/publish.yml/badge.svg)](https://github.com/happydev-ca/spypoint-api/actions/workflows/publish.yml)

# spypoint-api

Library to communicate with Spypoint REST API.

## Usage

```python
import aiohttp
import asyncio
import os

from spypointapi import SpypointApi


async def run():
    async with aiohttp.ClientSession() as session:
        api = SpypointApi(os.environ['EMAIL'], os.environ['PASSWORD'], session)

        cameras = await api.async_get_cameras()
        for camera in cameras:
            print(camera)


asyncio.run(run())
```

### Build and test locally

```shell
make venv
source .venv/bin/activate
make test
make build
```

### Logging

Enable debug level to log API requests and responses.
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Release version

```shell
make release bump=patch|minor|major
```
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

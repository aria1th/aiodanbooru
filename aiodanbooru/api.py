from typing import List

import aiohttp

from aiodanbooru.models import DanbooruPost
from logging import getLogger

class DanbooruAPI:
    def __init__(self, base_url: str = "https://danbooru.donmai.us"):
        self.base_url = base_url

    async def _get(
        self, session: aiohttp.ClientSession, endpoint: str, params: dict = None
    ) -> dict:
        url = self.base_url + endpoint
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def _post(
        self, session: aiohttp.ClientSession, endpoint: str, data: dict
    ) -> dict:
        url = self.base_url + endpoint
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()

    async def get_posts(
        self, tags: List[str] = None, limit: int = None
    ) -> List[DanbooruPost]:
        async with aiohttp.ClientSession() as session:
            endpoint = "/posts.json"
            params = {}
            if tags is not None:
                params["tags"] = " ".join(tags)
            if limit is not None:
                params["limit"] = str(limit)
            response = await self._get(session, endpoint, params)
            posts = [DanbooruPost(**post) for post in response]
            return posts

    async def get_random_post(self) -> DanbooruPost:
        async with aiohttp.ClientSession() as session:
            endpoint = "/posts/random.json"
            response = await self._get(session, endpoint)
            post = DanbooruPost(**response)
            return post

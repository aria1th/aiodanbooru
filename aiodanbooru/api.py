from typing import List

import aiohttp

from aiodanbooru.models import DanbooruPost
from logging import getLogger

class DanbooruAPI:
    def __init__(self, base_url: str = "https://danbooru.donmai.us", api_key: str = None, username: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.username = username
        self.POST_CLASS = DanbooruPost

    async def _get(
        self, session: aiohttp.ClientSession, endpoint: str, params: dict = None
    ) -> dict:
        # add api key to params
        if params is None:
            params = {}
        if self.api_key is not None:
            params["api_key"] = self.api_key
            params["login"] = self.username
        url = self.base_url + endpoint
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_post(
        self, id: int
    ) -> DanbooruPost:
        #https://danbooru.donmai.us/posts/<id>.json
        async with aiohttp.ClientSession() as session:
            endpoint = f"/posts/{id}.json"
            response = await self._get(session, endpoint)
            post = self.POST_CLASS(**response)
            return post
    
    async def get_posts_by_id(
        self, ids: List[int]
    ) -> List[DanbooruPost]:
        posts = []
        for id in ids:
            posts.append(await self.get_post(id))
        return posts

    async def _post(
        self, session: aiohttp.ClientSession, endpoint: str, data: dict
    ) -> dict:
        url = self.base_url + endpoint
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()

    async def get_posts(
        self, tags: List[str] = None, limit: int = None, page: int = None
    ) -> List[DanbooruPost]:
        async with aiohttp.ClientSession() as session:
            endpoint = "/posts.json"
            params = {}
            if tags is not None:
                params["tags"] = " ".join(tags)
            if limit is not None:
                params["limit"] = str(limit)
            if page is not None:
                params["page"] = str(page)
            response = await self._get(session, endpoint, params)
            posts = []
            for post in response:
                posts.append(self.POST_CLASS(**post)) 
            return posts
    
    async def get_posts_pages(
        self, tags: List[str] = None, limit: int = None, page_start: int = 1, page_end: int = 1
    ) -> List[DanbooruPost]:
        posts = []
        for page in range(page_start, page_end + 1):
            posts += await self.get_posts(tags=tags, limit=limit, page=page)
        # remove duplicates with id
        posts = list({post.id:post for post in posts}.values())
        return posts
    
    async def get_all_posts(
        self, tags: List[str] = None, limit: int = None
    ) -> List[DanbooruPost]:
        posts = []
        page = 1
        while True:
            try:
                new_posts = await self.get_posts(tags=tags, limit=limit, page=page)
            except Exception as exception:
                break # no more pages
            if not new_posts:
                break
            posts += new_posts
            page += 1
        # remove duplicates with id
        posts = list({post.id:post for post in posts}.values())
        # limit
        if limit is not None:
            posts = posts[:limit]
        return posts

    async def get_random_post(self) -> DanbooruPost:
        async with aiohttp.ClientSession() as session:
            endpoint = "/posts/random.json"
            response = await self._get(session, endpoint)
            post = self.POST_CLASS(**response)
            return post

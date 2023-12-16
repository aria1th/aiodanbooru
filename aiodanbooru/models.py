from typing import Optional, List

import aiohttp
from pydantic import BaseModel, Field
from pydantic.networks import HttpUrl

class DanbooruPost(BaseModel):
    id: int = Field(..., description="The ID of the post")
    uploader_id: int = Field(..., description="The ID of the uploader")
    approver_id: Optional[int] = Field(None, description="The ID of the approver")
    tag_string: str = Field(..., description="The tags of the post")
    tag_string_general: str = Field(..., description="The general tags of the post")
    tag_string_artist: str = Field(..., description="The artist tags of the post")
    tag_string_copyright: str = Field(..., description="Optional copyrights, such as animation")
    tag_string_character: str = Field(..., description="The character tags of the post")
    tag_string_meta: str = Field(..., description="The meta tags of the post")
    rating: Optional[str] = Field(None, description="The rating of the post")
    parent_id: Optional[int] = Field(None, description="The ID of the parent post")
    source: Optional[str] = Field(None, description="The source of the post")
    md5: Optional[str] = Field(None, description="MD5 hash of the media file")
    file_url: Optional[HttpUrl] = Field(None, description="URL of the media file")
    large_file_url: Optional[HttpUrl] = Field(
        None, description="URL of the large version of the media file"
    )
    preview_file_url: Optional[HttpUrl] = Field(
        None, description="URL of the preview version of the media file"
    )
    file_ext: Optional[str] = Field(None, description="The extension of the media file")
    file_size: Optional[int] = Field(None, description="The size of the media file")
    image_width: Optional[int] = Field(None, description="The width of the media file")
    score: int = Field(..., description="The score of the post")
    fav_count: int = Field(..., description="The number of favorites")
    tag_count_general: int = Field(..., description="The number of general tags")
    tag_count_artist: int = Field(..., description="The number of artist tags")
    tag_count_copyright: int = Field(..., description="The number of copyrights")
    tag_count_character: int = Field(..., description="The number of character tags")
    tag_count_meta: int = Field(..., description="The number of meta tags")
    last_comment_bumped_at: Optional[str] = Field(..., description="The last comment bumped at")
    last_noted_at: Optional[str] = Field(..., description="The last noted at")
    has_children: bool = Field(..., description="Whether the post has children")
    image_height: Optional[int] = Field(None, description="The height of the media file")
    created_at: str = Field(..., description="The time the post was created at")
    updated_at: str = Field(..., description="The time the post was updated at")

    class Config:
        extra = "allow"

    @property
    def extension(self) -> Optional[str]:
        if self.large_file_url:
            return self.large_file_url.split("/")[-1].split(".")[-1]
        elif self.file_url:
            return self.file_url.split("/")[-1].split(".")[-1]
        # elif self.source:
        #     return (
        #         self.source.split("/")[-1].split(".")[-1]
        #         if "." in self.source
        #         else self.file_ext
        #     )
        else:
            return self.file_ext

    async def get_media(self, use_large: bool = True) -> bytes:
        if not self.file_url and not self.large_file_url and self.source:
            try:
                return await self._get_media_from_source()
            except Exception as execption:
                raise Exception(f"State : self.file_url and self.large_file_url is None, self.source is {self.source}, id is {self.id}") from execption
        url = (
            self.large_file_url if use_large and self.large_file_url else self.file_url
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()

    @property
    def tags(self) -> List[str]:
        return self.tag_string.split()

    @property
    def link(self):
        return f"https://danbooru.donmai.us/posts/{self.id}"

    @property
    def media_url(self):
        return (
            self.large_file_url if self.large_file_url else self.file_url or self.source
        )

    def is_video(self) -> bool:
        return self.extension in ["webm", "mp4"]

    def is_image(self) -> bool:
        return self.extension in ["jpg", "jpeg", "png", "webp"]

    def is_animation(self) -> bool:
        return self.extension in ["gif", "gifv"]

    def is_zip(self) -> bool:
        return self.extension in ["zip"]

    @property
    def filename(self):
        return f"{self.md5}.{self.extension}"

    async def _get_media_from_source(self):
        async with aiohttp.ClientSession() as session:
            if self.source.startswith("https://i.pximg.net"):
                url = self.source.replace("i.pximg.net", "i.pixiv.cat")
            elif self.source.startswith("file://"):
                return b""
            else:
                url = self.source
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()

    async def get_metadata(self):
        """
        Returns all the other information except the media file.
        """
        return self.dict()
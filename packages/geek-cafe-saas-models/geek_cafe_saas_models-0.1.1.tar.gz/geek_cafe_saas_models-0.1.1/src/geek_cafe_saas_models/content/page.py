"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.
"""

from typing import List, Dict, Any
import datetime as dt
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey
from ._cms_base import BaseCMSDBModel
from .page_indexes import Indexes

class Page(BaseCMSDBModel):
    """
    A Page is generic term for a web page, blog post, news, product page etc.
    It's what defines the url, title, description, keywords, etc.
    A page is bound to template, which defines its look and feel.  The specific template
    will define header, footer, etc. and the build is the end product of this and its content.

    """

    def __init__(self) -> None:
        super().__init__()

        self.site_id: str | None = None
        """Partition Key"""
        self.template_id: str | None = None
        """Sort Key"""
        self.__slug: str | None = None
        """url"""
        self.title: str | None = None
        self.type: str | None = None
        """Page,Blog Post, etc."""
        self.description: str | None = None
        self.keywords: List[str] = []
        self.category: str | None = None
        self.tags: List[str] = []
        self.scopes: List[str] = ["public"]
        self.published_utc: dt.datetime | None = None
        self.scheduled_utc: dt.datetime | None = None
        self.expires_utc: dt.datetime | None = None        
        self.blocks: List[str] = []
        """List of block ids"""
        self.__setup_indexes()

    

    @property
    def id(self) -> str:
        """The id for the page"""
        return f"{self.site_id}/{self.type}/{self.slug}"

    @id.setter
    def id(self, id: str):
        pass

    @property
    def slug(self) -> str:
        """The slug (path) for the page"""
        return self.__slug

    @slug.setter
    def slug(self, slug: str):
        if not str(slug).startswith("/"):
            slug = f"/{slug}"

        if len(slug) > 1024:
            raise ValueError(
                "The slug is too long. "
                "It's used as a sort key which means it needs to be less than 1024 characters"
            )

        self.__slug = slug

    @property
    def s3_object_key(self) -> str:
        """The s3 object key for the page"""
        return f"{self.site_id}/{self.slug}"

    @s3_object_key.setter
    def s3_object_key(self, s3_object_key: str):
        pass

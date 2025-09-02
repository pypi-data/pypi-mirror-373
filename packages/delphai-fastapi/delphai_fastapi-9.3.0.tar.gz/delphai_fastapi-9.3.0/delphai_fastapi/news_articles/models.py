from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from ..models import CamelModel, Label
from ..types import ObjectId


class NewsArticleType(str, Enum):
    NEWS = "news"
    PRESS_RELEASE = "press release"


class NewsInclude(str, Enum):
    COMPANY_URL = "companyUrl"
    COMPANY_INTAPP_ID = "companyIntappId"


class NewsArticle(CamelModel):
    id: ObjectId = Field(..., description="Internal news article ID")
    company_id: ObjectId = Field(..., description="Internal company ID")
    company_intapp_id: Optional[UUID] = Field(
        default=None, description="Intapp ID of the company"
    )
    company_url: Optional[str] = Field(
        default=None, description="Webpage of the company", examples=["intapp.com"]
    )
    url: str = Field(
        ...,
        description="Article URL",
        examples=["https://airbridge.nl/sale-of-delphai-to-intapp-nasdaq-inta"],
    )
    type: NewsArticleType = Field(..., description="Type of article")
    published: datetime = Field(..., description="When the article was published")
    snippet: str = Field(
        ..., description="Snippet of the article mentioning the company"
    )
    language: Optional[str] = Field(
        None,
        description="Original language of the article in ISO 639 code",
        examples=["en"],
    )
    labels: Optional[List[Label]] = None
    title: str = Field(
        ..., description="Article title", examples=["Sale of delphai to Intapp"]
    )
    added: datetime = Field(..., description="When the article was added to delphai")
    data_provider: Optional[str] = Field(
        default="Intapp",
        description="Indicates whether the news article content was sourced internally by Intapp or from a third-party provider",  # noqa: E501
        examples=["Intapp"],
    )


class NewsArticles(CamelModel):
    results: List[NewsArticle]
    total: int = Field(..., description="Number of results")

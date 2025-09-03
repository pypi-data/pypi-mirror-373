import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field

from ..models import CamelModel
from ..types import ObjectId


class FundingAmountType(str, Enum):
    ORIGINAL = "original"
    CONVERTED = "converted"


class FundingAmountEntry(CamelModel):
    currency: str = Field(description="Currency of funding number", examples=["EUR"])
    value: int = Field(description="Funding number", examples=[1500000])
    type: FundingAmountType


class Investor(CamelModel):
    name: str = Field(..., description="Investor name", examples=["Intapp"])
    company_id: Optional[ObjectId] = Field(
        None, description="Internal Investor company ID"
    )


class FundingRound(CamelModel):
    id: ObjectId = Field(..., description="Internal FundingRound ID")
    company_id: ObjectId = Field(..., description="Internal company ID")
    amounts: Optional[Dict[str, FundingAmountEntry]] = Field(
        None, description="Original and converted funding numbers with currencies"
    )
    stage: Optional[str] = Field(
        None, description="Funding round stage", examples=["Series A"]
    )
    date: datetime.date = Field(
        ..., description="Date when the funding round was closed"
    )
    updated_at: Optional[datetime.datetime] = Field(
        None, description="Date and time when the funding round was updated"
    )
    investors: Optional[List[Investor]] = Field(
        None, description="List of investors in the funding round"
    )


class FundingRounds(CamelModel):
    results: List[FundingRound]
    total: int = Field(..., description="Number of results")

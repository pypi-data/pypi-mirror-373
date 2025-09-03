import datetime
from typing import List, Optional, Union

from pydantic import Field, model_validator

from ..models import CamelModel, InvestorType
from ..types import ObjectId


class RevenueEntry(CamelModel):
    id: ObjectId = Field(description="Internal revenue ID")
    company_id: ObjectId = Field(..., description="Internal company ID")
    currency: str = Field(description="Currency of revenue number", examples=["EUR"])
    annual: Optional[float] = Field(
        None, description="Annual revenue number for specified year", examples=[5000000]
    )
    year: Optional[int] = Field(
        None, description="Year of revenue number", examples=[2022]
    )
    gross_profit: Optional[float] = Field(
        None, description="Gross profit amount datapoint", examples=[50000]
    )
    ebit: Optional[float] = Field(
        None, description="EBIT amount datapoint", examples=[50000]
    )
    net_income: Optional[float] = Field(
        None, description="Net income amount datapoint", examples=[50000]
    )
    snippet: Optional[str] = Field(
        None,
        description="Text snippet mentioned a revenue data point",
        examples=["During fiscal 2020, we generated total revenues of $524.0 billion."],
    )
    approximation: Optional[str] = Field(
        None,
        description="Approximation symbol of revenue amount datapoint",
        examples=[
            "<",
        ],
    )
    sources: List[str] = Field(
        ..., description="Sources of data points", examples=[["yahoo_finance"]]
    )
    updated_at: datetime.datetime = Field(
        ..., description="Timestamp at which this datapoint got updated"
    )

    @model_validator(mode="before")
    @classmethod
    def format_fields(cls, values):
        if "_id" in values and "id" not in values:
            values["id"] = str(values.pop("_id"))
        if "revenue" in values and "annual" not in values:
            values["annual"] = values.pop("revenue")
        return values


class RevenueEntryCreate(CamelModel):
    company_id: str = Field(
        ..., description="Internal company ID", examples=["5ecd2d2d0faf391eadb211a7"]
    )
    currency: str = Field(
        ..., description="Currency of revenue number", examples=["EUR"]
    )
    year: Optional[int] = Field(
        None, description="Year of revenue number", examples=[2022]
    )
    gross_profit: Optional[float] = Field(
        None, description="Gross profit amount datapoint", examples=[50000]
    )
    ebit: Optional[float] = Field(
        None, description="EBIT amount datapoint", examples=[50000]
    )
    net_income: Optional[float] = Field(
        None, description="Net income amount datapoint", examples=[50000]
    )
    snippet: Optional[str] = Field(
        None,
        description="Text snippet mentioned a revenue data point",
        examples=["During fiscal 2020, we generated total revenues of $524.0 billion."],
    )
    approximation: Optional[str] = Field(
        None,
        description="Approximation symbol of revenue amount datapoint",
        examples=[
            "<",
        ],
    )
    source: str = Field(
        ..., description="Source of data points", examples=["yahoo_finance"]
    )
    revenue: Union[float, str, None] = Field(
        None, description="Revenue amount datapoint", examples=["22m"]
    )

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values):
        if not any(
            values.get(field)
            for field in ["revenue", "gross_profit", "ebit", "net_income"]
        ):
            raise ValueError(
                "At least one of revenue, gross_profit, ebit, or net_income must be present."
            )
        return values


class RevenueEntries(CamelModel):
    results: List[RevenueEntry]
    total: int = Field(..., description="Number of results", examples=[337])


class FundingEvent(CamelModel):
    company_id: ObjectId = Field(
        ..., description="Internal company ID", examples=["5ecd2d2d0faf391eadb211a7"]
    )
    source: str = Field(
        ..., description="Source of data points", examples=["yahoo_finance"]
    )
    investor_types: List[InvestorType]
    investor_id: Optional[ObjectId] = Field(
        None, description="Internal investor ID", examples=["5ecd2d2d0faf391eadb211a7"]
    )
    currency: Optional[str] = Field(
        None, description="Currency of amount of investment", examples=["EUR"]
    )
    amount: Optional[float] = Field(
        None, description="Amount of investment", examples=[15000000]
    )
    date: Optional[datetime.date] = Field(
        None, description="Date of the investment", examples=["2023-12-31"]
    )
    exit_date: Optional[datetime.date] = Field(
        None,
        description="Date the investor sold its part of the company",
        examples=["2023-12-31"],
    )
    investor_name: Optional[str] = Field(
        None, description="Name of the investor", examples=["Intapp"]
    )
    investor_url: Optional[str] = Field(
        None, description="Website of the investor", examples=["intapp.com"]
    )


class FundingEvents(CamelModel):
    results: List[FundingEvent]
    total: int = Field(..., description="Number of results", examples=[337])

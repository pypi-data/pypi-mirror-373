from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, BaseModel, Field, model_validator, field_validator
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class HTTPExceptionModel(CamelModel):
    detail: str


class Label(CamelModel):
    name: str = Field(description="Assigned label")
    children: List["Label"] = Field(description="Sublabels")


class Location(CamelModel):
    country: Optional[str] = Field(
        None, description="Company address (country)", examples=["United States"]
    )
    city: Optional[str] = Field(
        None, description="Company address (city)", examples=["Palo Alto"]
    )
    continent: Optional[str] = Field(
        None, description="Company address (continent)", examples=["North America"]
    )
    state: Optional[str] = Field(
        None, description="Company address (state/land)", examples=["California"]
    )
    latitude: Optional[float] = Field(None, examples=[37.4291])
    longitude: Optional[float] = Field(None, examples=[-122.1380])
    zip_code: Optional[str] = Field(
        None, description="Company address (ZIP code)", examples=["94306"]
    )


class EmployeeCount(CamelModel):
    min: Optional[int] = Field(
        None, description="Bottom range of the employee count interval", examples=[1001]
    )
    max: Optional[int] = Field(
        None, description="Top range of the employee count interval", examples=[5000]
    )
    exact: Optional[int] = Field(
        None,
        description="Exact number for employees",
        examples=[3000],
        validation_alias="n",
    )
    range: Optional[str] = Field(
        None,
        description="Employee count interval displayed in delphai",
        examples=["1,001-5,000"],
    )

    @model_validator(mode="after")
    def calculate_range(self):
        if self.range or not self.min:
            return self

        if self.max == self.min:
            self.range = str(format(self.min, ",d"))
        elif not self.max:
            self.range = str(format(self.min, ",d")) + "+"
        else:
            self.range = str(format(self.min, ",d")) + "-" + str(format(self.max, ",d"))
        return self

    @field_validator("max", mode="after")
    @classmethod
    def set_max_to_none_if_zero(cls, value):
        return value or None


class Source(CamelModel):
    name: str = Field(description="Name of the source")
    credibility_score: float = Field(
        description="Credibility score of source in percentage", examples=[0.60]
    )


class RelationType(str, Enum):
    ACQUISITION = "acquisition"
    PARTIAL_ACQUISITION = "partial_acquisition"
    FUNDING = "funding"
    SUBSIDIARY = "subsidiary"
    DIVESTMENT = "divestment"
    ADVISORY = "advisory"
    COMPETITOR = "competitor"
    CLIENT_SUPPLIER = "client_supplier"
    PARTNERSHIP = "partnership"
    LEGAL_ACTION = "legal_action"


class RelationTypeInternal(str, Enum):
    REGIONAL_WEBSITE = "regional_website"
    ALTERNATE_WEBSITE = "alternate_website"
    REBRAND = "rebrand"
    COMPANY_DIVISION = "company_division"
    SUBDOMAIN = "subdomain"
    REDIRECTED = "redirected"
    DUPLICATED_BY_EXTERNAL_ID = "duplicated_by_external_id"
    DUPLICATION_BY_URL = "duplication_by_url"
    SHAREHOLDER = "shareholder"


class Ownership(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class InvestorType(str, Enum):
    PRIVATE_EQUITY = "Private equity"
    VENTURE_CAPITAL = "Venture capital"
    FAMILY_OFFICE = "Family office"
    SOVEREIGN_FUND = "Sovereign fund"
    ASSET_MANAGER = "Asset manager"
    FINANCIAL = "Financial"
    STRATEGIC = "Strategic"

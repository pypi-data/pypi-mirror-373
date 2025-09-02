import datetime
import uuid
from ..models import CamelModel
from ..types import ObjectId
from typing import Optional, Dict, List
from enum import Enum

from pydantic import Field

PersonIdentifierCategory = str
PersonIdentifierSubcategory = str
PersonIdentifier = Dict[PersonIdentifierSubcategory, str]


class TransitionsInclude(str, Enum):
    COMPANY_URL = "companyUrl"
    PERSON_LINKEDIN = "personLinkedin"


class Person(CamelModel):
    id: ObjectId = Field(
        ...,
        description="Internal person ID",
        examples=["5ba3b37eb6fa1e372f53d049"],
    )
    first_name: Optional[str] = Field(
        default=None,
        description="First name of the person",
        examples=["John"],
    )
    last_name: Optional[str] = Field(
        default=None,
        description="Last name of the person",
        examples=["Doe"],
    )
    identifiers: Optional[Dict[PersonIdentifierCategory, PersonIdentifier]] = Field(
        None, description="Object of person identifiers"
    )
    linkedin_url: Optional[str] = Field(
        default=None, description="Link to the LinkedIn profile of the person"
    )


class PersonCreate(Person):
    id: Optional[ObjectId] = Field(
        default=None,
        description="Internal person ID",
        examples=["5ba3b37eb6fa1e372f53d049"],
    )
    source: str = Field(..., description="Source of person data", examples=["Equilar"])


class Position(CamelModel):
    start_date: Optional[datetime.date] = Field(
        None,
        description="Start date of the position",
        examples=["2023-12-31"],
    )
    end_date: Optional[datetime.date] = Field(
        None,
        description="End date of the position",
        examples=["2024-12-31"],
    )
    title: Optional[str] = Field(
        default=None,
        description="Title of the position",
        examples=["Senior Software Engineer"],
    )
    company_id: uuid.UUID = Field(
        ...,
        description="Company ID of the company associated with this position",
    )
    company_url: Optional[str] = Field(
        None,
        description="Webpage of the company associated with this position",
        examples=["intapp.com"],
    )
    person_id: Optional[ObjectId] = Field(
        default=None,
        description="Internal person ID of the person associated with this position",
    )
    person_name: Optional[str] = Field(
        default=None,
        description="Name of the person associated with this position",
        examples=["John Doe"],
    )
    person_linkedin: Optional[str] = Field(
        default=None, description="Link to the LinkedIn profile of the person"
    )
    data_provider: Optional[str] = Field(
        default="Intapp",
        description="Indicates whether the data was sourced internally by Intapp or from a third-party provider",  # noqa: E501
        examples=["Intapp"],
    )


class Transition(CamelModel):
    preceding_position: Optional[Position] = Field(
        default=None,
        description="Preceeding job position the person transitioned out of",
    )
    successive_position: Optional[Position] = Field(
        default=None,
        description="Successive job position the person transitioned to",
    )


class Transitions(CamelModel):
    results: List[Transition]
    total_results: int = Field(..., description="Total number of results")

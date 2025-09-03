from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ..models import CamelModel
from ..types import ObjectId


class JobDescription(CamelModel):
    default: str = Field(..., description="Description of the postion")
    original: Optional[str] = Field(
        None, description="Original description of the position"
    )


class JobClassification(CamelModel):
    isco_code: int = Field(..., description="ISCO code of the position", examples=[214])
    delphai_label: str = Field(
        ..., description="Label of the position", examples=["R&D"]
    )


class JobPostMinimal(CamelModel):
    url: str = Field(
        ...,
        description="Job post URL",
        examples=["https://join.com/companies/delphai/8943891-devops-engineer"],
    )
    published: datetime = Field(..., description="When the job post was published")
    title: str = Field(..., description="Position title", examples=["DevOps Engineer"])
    location: Optional[str] = Field(
        None, description="Location of the position", examples=["Berlin, Germany"]
    )
    language: Optional[str] = Field(
        None, description="Original language of the job post", examples=["en"]
    )
    deactivated: Optional[datetime] = Field(
        None, description="When the job post deactivated"
    )


class JobPost(JobPostMinimal):
    job_post_id: ObjectId = Field(..., description="Internal job post ID")
    company_id: ObjectId = Field(..., description="Internal company ID")
    added: datetime = Field(..., description="When the job post was added to delphai")
    is_active: bool = Field(..., description="Whether the job post is active or not")
    job_description: Optional[str] = Field(
        None, description="Description of the position"
    )
    description: Optional[JobDescription] = None
    classifications: Optional[List[JobClassification]] = None


class JobPostCreate(JobPostMinimal):
    company_name: str = Field(
        ...,
        description="Name of the company posting the job post",
        examples=["Intapp"],
    )
    added_by: str = Field(
        ...,
        description="ID of the process or person this job post was added by",
        examples=["job-posts-pipeline"],
    )
    source: str = Field(
        ..., description="Source of the job post", examples=["linkedin.com"]
    )
    company_id: Optional[ObjectId] = Field(None, description="Internal company ID")
    original_description: Optional[str] = Field(
        None, description="Description in original language"
    )
    translated_description: Optional[str] = Field(
        None,
        description="Translated description in english. Only necessary if original language is not english",
    )
    html_blob_reference: Optional[str] = Field(
        None, description="Reference to the blob that stores the HTML of the job post"
    )
    name_matched: Optional[bool] = Field(
        None,
        description="Whether the company of the job post was assigned using the names-matcher",
    )
    company_url: Optional[str] = Field(
        None,
        description="URL of the company posting the job post",
        examples=["intapp.com"],
    )
    country: Optional[str] = Field(
        None, description="Country of the position", examples=["United States"]
    )
    state: Optional[str] = Field(
        None, description="State of the position", examples=["California"]
    )
    city: Optional[str] = Field(
        None, description="City of the position", examples=["Palo Alto"]
    )
    isco_code: Optional[int] = Field(
        None, description="ISCO code of the position", examples=["214"]
    )


class JobPosts(CamelModel):
    results: List[JobPost]
    total: int = Field(..., description="Number of results")

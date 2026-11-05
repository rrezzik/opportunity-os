from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceText(StrictModel):
    value: str | None
    quote: str | None


class EvidenceItem(StrictModel):
    value: str
    quote: str | None


class PostingExtraction(StrictModel):
    company: EvidenceText
    title: EvidenceText
    location: EvidenceText
    compensation: EvidenceText
    employment_type: EvidenceText
    posting_date: EvidenceText
    work_arrangement: EvidenceText
    source_identifier: str
    source_url: str
    responsibilities: list[EvidenceItem]
    required_qualifications: list[EvidenceItem]
    preferred_qualifications: list[EvidenceItem]
    technologies: list[EvidenceItem]
    seniority: EvidenceText
    suggested_role_family: EvidenceText


class SourceRequest(StrictModel):
    url: str = Field(min_length=1)


class SourcePackage(StrictModel):
    source_url: str
    source_identifier: str
    source_label: str
    cleaned_text: str
    prompt: str


class ExtractionSubmission(StrictModel):
    expected_source_url: str
    raw_json: str = Field(min_length=1)


class ValidationResponse(StrictModel):
    extraction: PostingExtraction

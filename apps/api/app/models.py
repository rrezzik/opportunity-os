from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceText(StrictModel):
    value: str | None
    supporting_source_text: str | None
    confidence: Literal["low", "medium", "high"] | None

    @model_validator(mode="after")
    def evidence_matches_value(self) -> "EvidenceText":
        if self.value is None:
            if self.supporting_source_text is not None or self.confidence is not None:
                raise ValueError(
                    "Missing values cannot have supporting source text or confidence."
                )
        elif self.supporting_source_text is None or self.confidence is None:
            raise ValueError(
                "Extracted values require supporting source text and confidence."
            )
        return self


class EvidenceItem(StrictModel):
    value: str = Field(min_length=1)
    supporting_source_text: str = Field(min_length=1)
    confidence: Literal["low", "medium", "high"]


class PostingExtraction(StrictModel):
    schema_version: Literal["1.0"]
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
    source_format_version: Literal["1.0"]
    source_url: str
    source_identifier: str
    source_label: str
    raw_source: str
    cleaned_source: str
    prompt: str


class ExtractionSubmission(StrictModel):
    expected_source_url: str
    canonical_cleaned_source: str = Field(min_length=1)
    raw_json: str = Field(min_length=1)


class ValidationResponse(StrictModel):
    extraction: PostingExtraction

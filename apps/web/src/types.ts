export type EvidenceText = {
  value: string | null;
  supporting_source_text: string | null;
  confidence: "low" | "medium" | "high" | null;
};

export type EvidenceItem = {
  value: string;
  supporting_source_text: string;
  confidence: "low" | "medium" | "high";
};

export type PostingExtraction = {
  schema_version: "1.0";
  company: EvidenceText;
  title: EvidenceText;
  location: EvidenceText;
  compensation: EvidenceText;
  employment_type: EvidenceText;
  posting_date: EvidenceText;
  work_arrangement: EvidenceText;
  source_identifier: string;
  source_url: string;
  responsibilities: EvidenceItem[];
  required_qualifications: EvidenceItem[];
  preferred_qualifications: EvidenceItem[];
  technologies: EvidenceItem[];
  seniority: EvidenceText;
  suggested_role_family: EvidenceText;
};

export type SourcePackage = {
  id: string;
  source_format_version: "1.0";
  source_url: string;
  source_identifier: string;
  source_label: string;
  captured_at: string;
  raw_source: string;
  cleaned_source: string;
  content_sha256: string;
  prompt: string;
};

export type ProvisionalDraft = {
  id: string;
  capture_id: string;
  extraction_schema_version: "1.0";
  status: "provisional";
  created_at: string;
  extraction: PostingExtraction;
};

export type EvidenceText = {
  value: string | null;
  quote: string | null;
};

export type EvidenceItem = {
  value: string;
  quote: string | null;
};

export type PostingExtraction = {
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
  source_url: string;
  source_identifier: string;
  source_label: string;
  cleaned_text: string;
  prompt: string;
};

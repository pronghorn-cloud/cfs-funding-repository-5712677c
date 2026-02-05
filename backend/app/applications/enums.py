"""Application-related enumerations."""

from enum import StrEnum


class ApplicationStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUESTED = "additional_info_requested"
    REVIEWED = "reviewed"
    RECOMMENDED = "recommended"
    APPROVED = "approved"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"

    @classmethod
    def valid_transitions(cls) -> dict["ApplicationStatus", list["ApplicationStatus"]]:
        return {
            cls.DRAFT: [cls.SUBMITTED, cls.WITHDRAWN],
            cls.SUBMITTED: [cls.UNDER_REVIEW, cls.WITHDRAWN],
            cls.UNDER_REVIEW: [cls.ADDITIONAL_INFO_REQUESTED, cls.REVIEWED],
            cls.ADDITIONAL_INFO_REQUESTED: [cls.UNDER_REVIEW, cls.WITHDRAWN],
            cls.REVIEWED: [cls.RECOMMENDED, cls.DENIED],
            cls.RECOMMENDED: [cls.APPROVED, cls.DENIED],
            cls.APPROVED: [],
            cls.DENIED: [],
            cls.WITHDRAWN: [],
        }


class FundingType(StrEnum):
    OPERATIONAL = "operational"
    CAPITAL = "capital"
    EMERGENCY = "emergency"
    PROJECT_BASED = "project_based"


class ApplicationSectionType(StrEnum):
    ORGANIZATION_INFO = "organization_info"
    PROJECT_DESCRIPTION = "project_description"
    BUDGET = "budget"
    OUTCOMES = "outcomes"
    SUPPORTING_DOCUMENTS = "supporting_documents"

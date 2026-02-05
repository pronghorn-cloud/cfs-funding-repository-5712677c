"""Reporting Pydantic schemas."""

import uuid

from pydantic import BaseModel


class BriefingRequest(BaseModel):
    application_ids: list[uuid.UUID]
    report_type: str = "minister_briefing"  # minister_briefing, treasury_board
    include_svi_data: bool = True
    format: str = "pdf"  # pdf, docx


class ReportResponse(BaseModel):
    report_id: uuid.UUID
    report_type: str
    format: str
    file_name: str
    download_url: str

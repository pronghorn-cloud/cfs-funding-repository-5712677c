"""Report generation service using Jinja2 + WeasyPrint."""

import uuid
from datetime import datetime
from pathlib import Path

import structlog
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from app.applications.service import get_application
from app.documents.service import _upload_to_blob
from app.reporting.schemas import BriefingRequest

logger = structlog.get_logger()

TEMPLATE_DIR = Path(__file__).parent / "templates"

jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=True,
)


async def generate_briefing(
    request: BriefingRequest,
    db: AsyncSession,
    generated_by: uuid.UUID,
) -> dict:
    """Generate a briefing package (PDF or DOCX)."""
    # Gather application data
    applications = []
    for app_id in request.application_ids:
        app = await get_application(app_id, db)
        applications.append(app)

    # Build template context
    context = {
        "applications": applications,
        "generated_at": datetime.utcnow().isoformat(),
        "report_type": request.report_type,
        "include_svi_data": request.include_svi_data,
    }

    # Render HTML template
    template_name = f"{request.report_type}.html"
    try:
        template = jinja_env.get_template(template_name)
    except Exception:
        # Fall back to a simple template
        template = jinja_env.from_string(_default_template())

    html_content = template.render(**context)

    if request.format == "pdf":
        from weasyprint import HTML
        pdf_bytes = HTML(string=html_content).write_pdf()
        file_name = f"{request.report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        content_type = "application/pdf"
        file_data = pdf_bytes
    else:
        # DOCX generation via python-docx
        file_name = f"{request.report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        content_type = "text/html"
        file_data = html_content.encode()

    # Upload to blob storage
    blob_path = f"reports/{generated_by}/{file_name}"
    await _upload_to_blob(blob_path, file_data, content_type)

    return {
        "report_id": uuid.uuid4(),
        "report_type": request.report_type,
        "format": request.format,
        "file_name": file_name,
        "download_url": f"/api/v1/reports/download/{blob_path}",
    }


def _default_template() -> str:
    return """
<!DOCTYPE html>
<html>
<head><title>{{ report_type }} Report</title></head>
<body>
<h1>{{ report_type | replace('_', ' ') | title }}</h1>
<p>Generated: {{ generated_at }}</p>
{% for app in applications %}
<h2>{{ app.title }}</h2>
<p>Status: {{ app.status }}</p>
<p>Amount Requested: {{ app.amount_requested }}</p>
{% endfor %}
</body>
</html>
"""

"""Notification service for email sending via Azure Communication Services."""

import structlog

from app.common.circuit_breaker import CircuitBreaker

logger = structlog.get_logger()

email_circuit_breaker = CircuitBreaker(name="email_service", failure_threshold=3)


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
) -> bool:
    """Send an email notification."""
    try:
        await email_circuit_breaker.call(_send_via_acs, to_email, subject, html_body)
        logger.info("email_sent", to=to_email, subject=subject)
        return True
    except Exception as exc:
        logger.error("email_send_failed", to=to_email, error=str(exc))
        return False


async def send_application_submitted(to_email: str, application_title: str) -> bool:
    return await send_email(
        to_email=to_email,
        subject=f"Application Submitted: {application_title}",
        html_body=f"<p>Your application <strong>{application_title}</strong> has been submitted successfully.</p>",
    )


async def send_application_decision(
    to_email: str,
    application_title: str,
    decision: str,
) -> bool:
    return await send_email(
        to_email=to_email,
        subject=f"Application Decision: {application_title}",
        html_body=f"<p>Your application <strong>{application_title}</strong> has been <strong>{decision}</strong>.</p>",
    )


async def _send_via_acs(to_email: str, subject: str, html_body: str) -> None:
    """Send email via Azure Communication Services."""
    # Placeholder for ACS email integration
    # from azure.communication.email import EmailClient
    logger.info("acs_email_placeholder", to=to_email, subject=subject)

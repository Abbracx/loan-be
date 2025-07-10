from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_fraud_notification_email(loan_id, user_email, amount, reasons):
    """Send email notification to admin when loan is flagged"""
    subject = f"Loan Application Flagged - {loan_id}"
    message = f"""
    A loan application has been flagged for review:
    
    User: {user_email}
    Amount: NGN {amount}
    Reasons: {', '.join(reasons)}
    
    Please review in the admin panel.
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['admin@example.com'],
            fail_silently=False,
        )
        logger.info(f"Admin notification sent for flagged loan - ID: {loan_id}")
        return f"Email sent for loan {loan_id}"
    except Exception as e:
        logger.error(f"Failed to send admin notification - ID: {loan_id}, Error: {str(e)}")
        raise

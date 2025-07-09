from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import LoanApplication, FraudFlag, LoanStatus

User = get_user_model()


class FraudDetectionService:
    @staticmethod
    def check_fraud(user, amount_requested):
        flags = []
        
        # Check 1: More than 3 loans in past 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        recent_loans = LoanApplication.objects.filter(
            user=user, 
            date_applied__gte=yesterday
        ).count()
        
        if recent_loans >= 3:
            flags.append("User submitted more than 3 loans in past 24 hours")
        
        # Check 2: Amount exceeds 5,000,000 NGN
        if amount_requested > 5000000:
            flags.append("Requested amount exceeds NGN 5,000,000")
        
        # Check 3: Email domain used by more than 10 users
        email_domain = user.email.split('@')[1]
        domain_users = User.objects.filter(email__endswith=f'@{email_domain}').count()
        
        if domain_users > 10:
            flags.append("Email domain used by more than 10 users")
        
        return flags

    @staticmethod
    def flag_loan(loan_application, reasons):
        loan_application.status = LoanStatus.FLAGGED
        loan_application.save()
        
        for reason in reasons:
            FraudFlag.objects.create(
                loan_application=loan_application,
                reason=reason
            )
        
        # Send email notification to admin
        FraudDetectionService.notify_admin(loan_application, reasons)

    @staticmethod
    def notify_admin(loan_application, reasons):
        subject = f"Loan Application Flagged - {loan_application.id}"
        message = f"""
        A loan application has been flagged for review:
        
        User: {loan_application.user.email}
        Amount: NGN {loan_application.amount_requested}
        Reasons: {', '.join(reasons)}
        
        Please review in the admin panel.
        """
        
        # Mock email sending - replace with actual implementation
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['admin@example.com'],  # Replace with actual admin emails
                fail_silently=True,
            )
        except Exception:
            pass  # Log error in production

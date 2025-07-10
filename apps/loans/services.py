import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from .models import LoanApplication, FraudFlag, LoanStatus
from .tasks import send_fraud_notification_email

User = get_user_model()
logger = logging.getLogger(__name__)


class FraudDetectionService:
    @staticmethod
    def check_fraud(user, amount_requested):
        flags = []
        logger.info(f"Running fraud detection - User: {user.id}, Amount: {amount_requested}")
        
        # Check 1: More than 3 loans in past 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        recent_loans = LoanApplication.objects.filter(
            user=user, 
            date_applied__gte=yesterday
        ).count()
        
        if recent_loans >= 3:
            flag = "User submitted more than 3 loans in past 24 hours"
            flags.append(flag)
            logger.warning(f"Fraud flag: {flag} - User: {user.id}")
        
        # Check 2: Amount exceeds 5,000,000 NGN
        if amount_requested > 5000000:
            flag = "Requested amount exceeds NGN 5,000,000"
            flags.append(flag)
            logger.warning(f"Fraud flag: {flag} - User: {user.id}, Amount: {amount_requested}")
        
        # Check 3: Email domain used by more than 10 users
        email_domain = user.email.split('@')[1]
        cache_key = f"domain_users_{email_domain}"
        domain_users = cache.get(cache_key)
        
        if domain_users is None:
            domain_users = User.objects.filter(email__endswith=f'@{email_domain}').count()
            cache.set(cache_key, domain_users, timeout=3600)
        
        if domain_users > 10:
            flag = "Email domain used by more than 10 users"
            flags.append(flag)
            logger.warning(f"Fraud flag: {flag} - User: {user.id}, Domain: {email_domain}")
        
        logger.info(f"Fraud detection completed - User: {user.id}, Flags: {len(flags)}")
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
        
        logger.error(f"Loan flagged - ID: {loan_application.id}, User: {loan_application.user.id}, Reasons: {reasons}")
        
        # Clear flagged loans cache
        cache.delete("flagged_loans_list")
        
        # Queue email notification
        send_fraud_notification_email.delay(
            str(loan_application.id),
            loan_application.user.email,
            str(loan_application.amount_requested),
            reasons
        )
        logger.info(f"Fraud notification email queued for Loan ID: {loan_application.id}, User: {loan_application.user.id}")
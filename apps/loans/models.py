from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from apps.common.models import TimeStampedModel

User = get_user_model()


class LoanStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')
    FLAGGED = 'flagged', _('Flagged')


class LoanApplication(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications', db_index=True)
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=LoanStatus.choices, default=LoanStatus.PENDING, db_index=True)
    date_applied = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-date_applied']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'date_applied']),
            models.Index(fields=['status', 'date_applied']),
            models.Index(fields=['amount_requested', 'status']),
            models.Index(fields=['date_applied', 'status']),
            models.Index(fields=['user', 'status', 'date_applied']),
            models.Index(fields=['status', 'amount_requested', 'date_applied']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.amount_requested}"


class FraudFlag(TimeStampedModel):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='fraud_flags', db_index=True)
    reason = models.CharField(max_length=255, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['loan_application', 'created_at']),
            models.Index(fields=['reason', 'created_at']),
            models.Index(fields=['loan_application', 'reason']),
        ]

    def __str__(self):
        return f"Flag: {self.reason}"

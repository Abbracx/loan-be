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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications')
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=LoanStatus.choices, default=LoanStatus.PENDING)
    date_applied = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_applied']

    def __str__(self):
        return f"{self.user.username} - {self.amount_requested}"


class FraudFlag(TimeStampedModel):
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='fraud_flags')
    reason = models.CharField(max_length=255)

    def __str__(self):
        return f"Flag: {self.reason}"

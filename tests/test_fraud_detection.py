import pytest
from django.utils import timezone
from datetime import timedelta
from apps.loans.services import FraudDetectionService
from apps.loans.models import LoanApplication, LoanStatus
from tests.factories import UserFactory, LoanApplicationFactory


@pytest.mark.django_db
class TestFraudDetection:
    def test_multiple_loans_fraud_detection(self):
        user = UserFactory()
        
        # Create 3 loans in the past 24 hours
        yesterday = timezone.now() - timedelta(hours=12)
        for _ in range(3):
            LoanApplicationFactory(user=user, date_applied=yesterday)
        
        # Check fraud for a new loan
        flags = FraudDetectionService.check_fraud(user, 1000000)
        assert "User submitted more than 3 loans in past 24 hours" in flags

    def test_high_amount_fraud_detection(self):
        user = UserFactory()
        flags = FraudDetectionService.check_fraud(user, 6000000)
        assert "Requested amount exceeds NGN 5,000,000" in flags

    def test_email_domain_fraud_detection(self):
        # Create 11 users with same domain
        domain = "suspicious.com"
        for i in range(11):
            UserFactory(email=f"user{i}@{domain}")
        
        test_user = UserFactory(email=f"test@{domain}")
        flags = FraudDetectionService.check_fraud(test_user, 1000000)
        assert "Email domain used by more than 10 users" in flags

    def test_loan_flagging(self):
        loan = LoanApplicationFactory()
        reasons = ["Test reason"]
        
        FraudDetectionService.flag_loan(loan, reasons)
        
        loan.refresh_from_db()
        assert loan.status == LoanStatus.FLAGGED
        assert loan.fraud_flags.count() == 1
        assert loan.fraud_flags.first().reason == "Test reason"

    # @pytest.mark.parametrize("reasons", [
    #     ["Test reason 1", "Test reason 2"],
    #     ["Another reason"],
    #     []
    # ])
    # def test_notify_admin(self, mocker):
    #     loan = LoanApplicationFactory()
    #     reasons = ["Test reason"]
        
    #     mock_send_mail = mocker.patch('apps.loans.services.FraudDetectionService.notify_admin')
    #     FraudDetectionService.flag_loan(loan, reasons)
        
    #     mock_send_mail.assert_called_once()
    #     args, kwargs = mock_send_mail.call_args
    #     assert args[0] == loan
    #     assert args[1] == reasons
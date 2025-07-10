import pytest
from django.urls import reverse
from rest_framework import status
from apps.loans.models import LoanApplication, LoanStatus
from tests.factories import UserFactory, LoanApplicationFactory


@pytest.mark.django_db
class TestLoanApplication:
    def test_successful_loan_submission(self, api_client, regular_user):
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan-applications-list')
        data = {
            'amount_requested': 1000000,
            'purpose': 'Business expansion'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        loan = LoanApplication.objects.get(id=response.data['id'])
        assert loan.user == regular_user
        assert loan.amount_requested == 1000000
        assert loan.status == LoanStatus.PENDING

    def test_user_can_only_view_own_loans(self, api_client):
        user1 = UserFactory()
        user2 = UserFactory()
        
        loan1 = LoanApplicationFactory(user=user1)
        loan2 = LoanApplicationFactory(user=user2)
        
        api_client.force_authenticate(user=user1)
        url = reverse('loans:loan-applications-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(loan1.id)

    def test_admin_can_approve_loan(self, api_client, admin_user):
        loan = LoanApplicationFactory()
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('loans:loan-applications-approve', kwargs={'pk': loan.pk})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        loan.refresh_from_db()
        assert loan.status == LoanStatus.APPROVED

    def test_regular_user_cannot_approve_loan(self, api_client, regular_user):
        loan = LoanApplicationFactory(user=regular_user)
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan-applications-approve', kwargs={'pk': loan.pk})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_flagged_loans_endpoint(self, api_client, admin_user):
        flagged_loan = LoanApplicationFactory(status=LoanStatus.FLAGGED)
        normal_loan = LoanApplicationFactory(status=LoanStatus.PENDING)
        
        api_client.force_authenticate(user=admin_user)
        url = reverse('loans:flagged-loans')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == str(flagged_loan.id)
    
    def test_fraud_detection_on_loan_creation(self, api_client, regular_user):
        api_client.force_authenticate(user=regular_user)
        url = reverse('loans:loan-applications-list')
        data = {
            'amount_requested': 6000000,  # Exceeds the limit
            'purpose': 'High value loan'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        loan = LoanApplication.objects.get(id=response.data['id'])
        assert loan.status == LoanStatus.FLAGGED
        assert loan.fraud_flags.count() > 0
        assert "Requested amount exceeds NGN 5,000,000" in loan.fraud_flags.first().reason 

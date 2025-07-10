import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserManagement:
    def test_create_user(self, user_factory):
        user = user_factory(username='newuser', email='new@example.com')
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('testpass123')

    def test_user_login(self, api_client, regular_user):
        url = reverse('usersauth:jwt-create')
        data = {
            'email': regular_user.email,
            'password': 'regularpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_user_profile_access(self, api_client, regular_user):
        api_client.force_authenticate(user=regular_user)
        url = reverse('usersapi:users-me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == regular_user.email

    def test_admin_user_access(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('usersapi:users-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data.get("results", None), list)
        assert len(response.data) > 0
    
    # def test_user_profile_update(self, api_client, regular_user):
    #     api_client.force_authenticate(user=regular_user)
    #     url = reverse('usersapi:users-me')
    #     data = {
    #         'first_name': 'Updated',
    #         'last_name': 'User',
    #         'phone_number': '+1234567890'
    #     }
    #     response = api_client.patch(url, data)
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.data['first_name'] == 'Updated'
    #     assert response.data['last_name'] == 'User'
    #     assert response.data['phone_number'] == '+1234567890'


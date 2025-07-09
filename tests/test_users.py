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

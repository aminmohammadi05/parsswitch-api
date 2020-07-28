from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the user api"""
    def setUp(self):
        self.client = APIClient()
    def test_create_valid_user_success(self):
        """Test creating valid user is successful"""
        payload = {
            'email' : 'amin_mohammadi05@yahoo.com',
            'password' : '1234567aA',
            'name' : 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertIn('password', res.data)
    
    def test_user_exists(self):
        """ Test creating a user that already exists """
        payload = {'email': 'amin_mohammadi05@yahoo.com', 'password': '1234567aA'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 charactes"""
        payload = {'email': 'amin_mohammadi05@yahoo.com', 'password': 'pw'}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@yahoo.com', 'password': '1234567aA',
            'name' : 'test'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    def test_create_token_invalid_credential(self):
        """Test that token is not created if the credential is not valid"""
        payload = {'email': 'amin_mohammadi05@yahoo.com', 'password': 'wrong'}
        create_user(email='amin_mohammadi05@yahoo.com', password='1234567aA')
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    def test_create_token_no_user(self):
        """Test that token is not created if the credential is not valid"""
        payload = {'email': 'amin_mohammadi05@yahoo.com', 'password': '1234567aA'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    def test_create_token_missing_field(self):
        """Test that token is not created if the credential is not valid"""
        payload = {
            'email' : 'one',
            'password' : '',
            'name' : 'test'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
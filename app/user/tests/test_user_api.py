from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

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
    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
class PrivateUserApiTests(TestCase):
    """Test Api requests that require authentication"""
    def setUp(self):
        self.user = create_user(
            email='amin_mohammadi05@yahoo.com',
            password='1234567aA',
            name='name')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name' : self.user.name,
            'password' : self.user.password,
            'email': self.user.email
        })
    def test_post_me_not_allowed(self):
        """Test that post is not allowed in the me"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    def test_update_user_profile(self):
        """Test update user profile for authenticating user"""
        payload = {
            'password' : 'new password',
            'name' : 'new name'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
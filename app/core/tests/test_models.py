from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='amin_mohammadi05@yahoo.com', password='1234567aA'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)

    
class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test Creating a new User with a email is successful"""
        email = "amin_mohammadi05@yahoo.com"
        password = "TestPass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for the new user is normalized"""
        email = "amin_mohammadi05@YAHOO.COM"
        user = get_user_model().objects.create_user(
            email,
            'test123',
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                'test123',
            )

    def test_create_new_superuser(self):
        """Test creating new super user"""
        email = "amin_mohammadi05@yahoo.com"
        user = get_user_model().objects.create_superuser(
            email,
            'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_product_str(self):
        """Test the product string respresentation"""
        product = models.Product.objects.create(
            user=sample_user(),
            name='FP'
        )

        self.assertEqual(str(product), product.name)

    # def test_category_str(self):
    #     """Test the category string representation"""
    #     category = models.Category.objects.create(
    #         user=sample_user(),
    #         title='HV'
    #     )

    #     self.assertEqual(str(category), category.title)

    # @patch('uuid.uuid4')
    # def test_product_file_name_uuid(self, mock_uuid):
    #     """Test that image is saved in the correct location"""
    #     uuid = 'test-uuid'
    #     mock_uuid.return_value = uuid
    #     file_path = models.product_image_file_path(None, 'myimage.jpg')

    #     exp_path = f'uploads/product/{uuid}.jpg'
    #     self.assertEqual(file_path, exp_path)

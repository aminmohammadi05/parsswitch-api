import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Category

from category.serializers import ProductSerializer


PRODUCTS_URL = reverse('category:product-list')
def image_upload_url(product_id):
    """Return URL for category image upload"""
    return reverse('category:product-upload-image', args=[product_id])
def detail_url(product_id):
    """Return product detail URL"""
    return reverse('category:product-detail', args=[product_id])




def sample_product(user, name='Cinnamon'):
    """Create and return a sample product"""
    return Product.objects.create(user=user, name=name)


def sample_category(user, **params):
    """Create and return a sample category"""
    defaults = {
        'name': 'Sample category',
        'persian_title': 'persian',
        'parent_category': None
    }
    defaults.update(params)

    return Category.objects.create(user=user, **defaults)

class PublicProductsApiTests(TestCase):
    """Test the publicly available products API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductsApiTests(TestCase):
    """Test the private products API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'amin_mohammadi05@yahoo.com',
            '1234567aA'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_product_list(self):
        """Test retrieving a list of products"""
        Product.objects.create(user=self.user, name='Kale', description='description')
        Product.objects.create(user=self.user, name='Salt', description='description')

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.all().order_by('-name')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_products_limited_to_user(self):
        """Test that products for the authenticated user are returend"""
        user2 = get_user_model().objects.create_user(
            'amin_mohammadi06@yahoo.com',
            '1234567aA'
        )
        Product.objects.create(user=user2, name='Kale', description='description')
        product = Product.objects.create(user=self.user, name='Tumeric', description='description')

        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], product.name)

    def test_create_product_successful(self):
        """Test create a new product"""
        payload = {'name': 'Cabbage', 'description': 'description', 'user': self.user}
        self.client.post(PRODUCTS_URL, payload)
        
        exists = Product.objects.filter(
            user=self.user,
            name=payload['name'],
            description='description'
        ).exists()
        self.assertTrue(exists)

    def test_create_product_invalid(self):
        """Test creating invalid product fails"""
        payload = {'name': ''}
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_view_product_detail(self):
    #     """Test viewing a category detail"""
    #     category = sample_category(user=self.user)
    #     category.products.add(sample_product(user=self.user))
    #     category.products.add(sample_product(user=self.user))

    #     url = detail_url(category.id)
    #     res = self.client.get(url)

    #     serializer = CategoryDetailSerializer(category)
    #     self.assertEqual(res.data, serializer.data)
#     def test_retrieve_products_assigned_to_categories(self):
#         """Test filtering products by those assigned to categories"""
#         product1 = Product.objects.create(
#             user=self.user, name='Apples'
#         )
#         product2 = Product.objects.create(
#             user=self.user, name='Turkey'
#         )
#         category = Category.objects.create(
#             title='Apple crumble',
#             time_minutes=5,
#             price=10,
#             user=self.user
#         )
#         category.products.add(product1)

#         res = self.client.get(PRODUCTS_URL, {'assigned_only': 1})

#         serializer1 = ProductSerializer(product1)
#         serializer2 = ProductSerializer(product2)
#         self.assertIn(serializer1.data, res.data)
#         self.assertNotIn(serializer2.data, res.data)

#     def test_retrieve_products_assigned_unique(self):
#         """Test filtering products by assigned returns unique items"""
#         product = Product.objects.create(user=self.user, name='Eggs')
#         Product.objects.create(user=self.user, name='Cheese')
#         category1 = Category.objects.create(
#             title='Eggs benedict',
#             time_minutes=30,
#             price=12.00,
#             user=self.user
#         )
#         category1.products.add(product)
#         category2 = Category.objects.create(
#             title='Coriander eggs on toast',
#             time_minutes=20,
#             price=5.00,
#             user=self.user
#         )
#         category2.products.add(product)

#         res = self.client.get(PRODUCTS_URL, {'assigned_only': 1})

#         self.assertEqual(len(res.data), 1)


class ProductImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.product = sample_product(user=self.user)

    def tearDown(self):
        self.product.image.delete()

    def test_upload_image_to_product(self):
        """Test uploading an email to product"""
        url = image_upload_url(self.product.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.product.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.product.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.product.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_filter_categories_by_products(self):
        """Test returning categories with specific products"""
        category1 = sample_category(user=self.user, title='Posh beans on toast')
        category2 = sample_category(user=self.user, title='Chicken cacciatore')
        product1 = sample_product(user=self.user, name='Feta cheese')
        product2 = sample_product(user=self.user, name='Chicken')
        category1.products.add(product1)
        category2.products.add(product2)
        category3 = sample_category(user=self.user, title='Steak and mushrooms')

        res = self.client.get(
            CATEGORIES_URL,
            {'products': f'{product1.id},{product2.id}'}
        )

        serializer1 = CategorySerializer(category1)
        serializer2 = CategorySerializer(category2)
        serializer3 = CategorySerializer(category3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
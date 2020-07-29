from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Category

from category.serializers import ProductSerializer


PRODUCTS_URL = reverse('category:product-list')


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
        category = Category.objects.create(
            user=self.user,
            name='HV',
            persian_title='HV'
        )
        Product.objects.create(user=self.user, name='Kale', category=category, description='description')
        Product.objects.create(user=self.user, name='Salt', category=category, description='description')

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
        category = Category.objects.create(
            user=self.user,
            name='HV',
            persian_title='HV'
        )
        Product.objects.create(user=user2, name='Kale', category=category, description='description')
        product = Product.objects.create(user=self.user, name='Tumeric', category=category, description='description')

        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], product.name)

    def test_create_product_successful(self):
        """Test create a new product"""
        category = Category.objects.create(user=self.user, name='MV')
        payload = {'name': 'Cabbage', 'category': category.id, 'description': 'description', 'user': self.user}
        self.client.post(PRODUCTS_URL, payload)
        
        exists = Product.objects.filter(
            user=self.user,
            name=payload['name'],
            description='description',
            category=category
        ).exists()
        self.assertTrue(exists)

    def test_create_product_invalid(self):
        """Test creating invalid product fails"""
        payload = {'name': ''}
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

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
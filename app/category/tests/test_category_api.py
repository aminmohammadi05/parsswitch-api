import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Product

from category.serializers import CategorySerializer


CATEGORIES_URL = reverse('category:category-list')


# def image_upload_url(category_id):
#     """Return URL for category image upload"""
#     return reverse('category:category-upload-image', args=[category_id])


# def detail_url(category_id):
#     """Return category detail URL"""
#     return reverse('category:category-detail', args=[category_id])




# def sample_product(user, name='Cinnamon'):
#     """Create and return a sample product"""
#     return Product.objects.create(user=user, name=name)


def sample_category(user, **params):
    """Create and return a sample category"""
    defaults = {
        'name': 'Sample category',
        'persian_title': 'persian',
        'parent_category': None
    }
    defaults.update(params)

    return Category.objects.create(user=user, **defaults)


class PublicCategoryApiTests(TestCase):
    """Test unauthenticated category API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryApiTests(TestCase):
    """Test unauthenticated category API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_categories(self):
        """Test retrieving a list of categories"""
        sample_category(user=self.user)
        sample_category(user=self.user)

        res = self.client.get(CATEGORIES_URL)

        categories = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(categories, many=True)
        print(serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_categories_limited_to_user(self):
        """Test retrieving categories for user"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'password123'
        )
        sample_category(user=user2)
        sample_category(user=self.user)

        res = self.client.get(CATEGORIES_URL)

        categories = Category.objects.filter(user=self.user)
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

#     def test_view_category_detail(self):
#         """Test viewing a category detail"""
#         category = sample_category(user=self.user)
#         category.tags.add(sample_tag(user=self.user))
#         category.products.add(sample_product(user=self.user))

#         url = detail_url(category.id)
#         res = self.client.get(url)

#         serializer = CategoryDetailSerializer(category)
#         self.assertEqual(res.data, serializer.data)

#     def test_create_basic_category(self):
#         """Test creating category"""
#         payload = {
#             'title': 'Chocolate cheesecake',
#             'time_minutes': 30,
#             'price': 5.00
#         }
#         res = self.client.post(CATEGORIES_URL, payload)

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         category = Category.objects.get(id=res.data['id'])
#         for key in payload.keys():
#             self.assertEqual(payload[key], getattr(category, key))

#     def test_create_category_with_tags(self):
#         """Test creating a category with tags"""
#         tag1 = sample_tag(user=self.user, name='Vegan')
#         tag2 = sample_tag(user=self.user, name='Dessert')
#         payload = {
#             'title': 'Avocado lime cheesecake',
#             'tags': [tag1.id, tag2.id],
#             'time_minutes': 60,
#             'price': 20.00
#         }
#         res = self.client.post(CATEGORIES_URL, payload)

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         category = Category.objects.get(id=res.data['id'])
#         tags = category.tags.all()
#         self.assertEqual(tags.count(), 2)
#         self.assertIn(tag1, tags)
#         self.assertIn(tag2, tags)

#     def test_create_category_with_products(self):
#         """Test creating category with products"""
#         product1 = sample_product(user=self.user, name='Prawns')
#         product2 = sample_product(user=self.user, name='Ginger')
#         payload = {
#             'title': 'Thai prawn red curry',
#             'products': [product1.id, product2.id],
#             'time_minutes': 20,
#             'price': 7.00
#         }
#         res = self.client.post(CATEGORIES_URL, payload)

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         category = Category.objects.get(id=res.data['id'])
#         products = category.products.all()
#         self.assertEqual(products.count(), 2)
#         self.assertIn(product1, products)
#         self.assertIn(product2, products)

#     def test_partial_update_category(self):
#         """Test updating a category with patch"""
#         category = sample_category(user=self.user)
#         category.tags.add(sample_tag(user=self.user))
#         new_tag = sample_tag(user=self.user, name='Curry')

#         payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
#         url = detail_url(category.id)
#         self.client.patch(url, payload)

#         category.refresh_from_db()
#         self.assertEqual(category.title, payload['title'])
#         tags = category.tags.all()
#         self.assertEqual(len(tags), 1)
#         self.assertIn(new_tag, tags)

#     def test_full_update_category(self):
#         """Test updating a category with put"""
#         category = sample_category(user=self.user)
#         category.tags.add(sample_tag(user=self.user))
#         payload = {
#             'title': 'Spaghetti carbonara',
#             'time_minutes': 25,
#             'price': 5.00
#         }
#         url = detail_url(category.id)
#         self.client.put(url, payload)

#         category.refresh_from_db()
#         self.assertEqual(category.title, payload['title'])
#         self.assertEqual(category.time_minutes, payload['time_minutes'])
#         self.assertEqual(category.price, payload['price'])
#         tags = category.tags.all()
#         self.assertEqual(len(tags), 0)


# class CategoryImageUploadTests(TestCase):

#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             'user@londonappdev.com',
#             'testpass'
#         )
#         self.client.force_authenticate(self.user)
#         self.category = sample_category(user=self.user)

#     def tearDown(self):
#         self.category.image.delete()

#     def test_upload_image_to_category(self):
#         """Test uploading an email to category"""
#         url = image_upload_url(self.category.id)
#         with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
#             img = Image.new('RGB', (10, 10))
#             img.save(ntf, format='JPEG')
#             ntf.seek(0)
#             res = self.client.post(url, {'image': ntf}, format='multipart')

#         self.category.refresh_from_db()
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertIn('image', res.data)
#         self.assertTrue(os.path.exists(self.category.image.path))

#     def test_upload_image_bad_request(self):
#         """Test uploading an invalid image"""
#         url = image_upload_url(self.category.id)
#         res = self.client.post(url, {'image': 'notimage'}, format='multipart')

#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_filter_categories_by_tags(self):
#         """Test returning categories with specific tags"""
#         category1 = sample_category(user=self.user, title='Thai vegetable curry')
#         category2 = sample_category(user=self.user, title='Aubergine with tahini')
#         tag1 = sample_tag(user=self.user, name='Vegan')
#         tag2 = sample_tag(user=self.user, name='Vegetarian')
#         category1.tags.add(tag1)
#         category2.tags.add(tag2)
#         category3 = sample_category(user=self.user, title='Fish and chips')

#         res = self.client.get(
#             CATEGORIES_URL,
#             {'tags': f'{tag1.id},{tag2.id}'}
#         )

#         serializer1 = CategorySerializer(category1)
#         serializer2 = CategorySerializer(category2)
#         serializer3 = CategorySerializer(category3)
#         self.assertIn(serializer1.data, res.data)
#         self.assertIn(serializer2.data, res.data)
#         self.assertNotIn(serializer3.data, res.data)

#     def test_filter_categories_by_products(self):
#         """Test returning categories with specific products"""
#         category1 = sample_category(user=self.user, title='Posh beans on toast')
#         category2 = sample_category(user=self.user, title='Chicken cacciatore')
#         product1 = sample_product(user=self.user, name='Feta cheese')
#         product2 = sample_product(user=self.user, name='Chicken')
#         category1.products.add(product1)
#         category2.products.add(product2)
#         category3 = sample_category(user=self.user, title='Steak and mushrooms')

#         res = self.client.get(
#             CATEGORIES_URL,
#             {'products': f'{product1.id},{product2.id}'}
#         )

#         serializer1 = CategorySerializer(category1)
#         serializer2 = CategorySerializer(category2)
#         serializer3 = CategorySerializer(category3)
#         self.assertIn(serializer1.data, res.data)
#         self.assertIn(serializer2.data, res.data)
#         self.assertNotIn(serializer3.data, res.data)
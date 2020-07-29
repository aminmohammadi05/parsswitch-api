from rest_framework import serializers

from core.models import Product, Category



class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'category')
        read_only_fields = ('id',)


# class CategorySerializer(serializers.ModelSerializer):
#     """Serialize a category"""
#     # categories = serializers.PrimaryKeyRelatedField(
#     #     many=True,
#     #     queryset=Category.objects.all()
#     # )
   
#     class Meta:
#         model = Category
#         fields = (
#             'id', 'name', 'persian_title', 'parent_category'
#         )
#         read_only_fields = ('id',)
class CategorySerializer(serializers.ModelSerializer):
    """Serialize a category"""
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'persian_title', 'parent_category'
        )
        read_only_fields = ('id',)

# class CategoryDetailSerializer(CategorySerializer):
#     """Serialize a category detail"""
#     products = ProductSerializer(many=True, read_only=True)


# class ProductImageSerializer(serializers.ModelSerializer):
#     """Serializer for uploading images to products"""

#     class Meta:
#         model = Product
#         fields = ('id', 'image')
#         read_only_fields = ('id',)
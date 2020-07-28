from rest_framework import serializers

from core.models import Product



class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    class Meta:
        model = Product
        fields = ('id', 'name')
        read_only_fields = ('id',)


# class CategorySerializer(serializers.ModelSerializer):
#     """Serialize a category"""
#     products = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=Product.objects.all()
#     )
   
#     class Meta:
#         model = Category
#         fields = (
#             'id', 'title', 'tags'
#         )
#         read_only_fields = ('id',)


# class CategoryDetailSerializer(CategorySerializer):
#     """Serialize a category detail"""
#     products = ProductSerializer(many=True, read_only=True)


# class ProductImageSerializer(serializers.ModelSerializer):
#     """Serializer for uploading images to products"""

#     class Meta:
#         model = Product
#         fields = ('id', 'image')
#         read_only_fields = ('id',)
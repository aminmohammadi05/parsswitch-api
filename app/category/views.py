
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Product, Category
from category import serializers

class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)

class ProductViewSet(BaseRecipeAttrViewSet):
    """Manage products in the database"""
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """Manage category in the database"""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer    
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(
            user=self.request.user
        )
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.CategoryDetailSerializer
        # elif self.action == 'upload_image':
        #     return serializers.RecipeImageSerializer

        return self.serializer_class
    def perform_create(self, serializer):
        """Create a new category"""
        serializer.save(user=self.request.user)
    


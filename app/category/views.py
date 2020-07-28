
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Product
from category import serializers



class ProductViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    """Manage products in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # assigned_only = bool(
        #     int(self.request.query_params.get('assigned_only', 0))
        # )
        # queryset = self.queryset
        # if assigned_only:
        #     queryset = queryset.filter(recipe__isnull=False)

        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')
    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


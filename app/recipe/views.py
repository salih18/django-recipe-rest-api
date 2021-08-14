from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage tags in the db"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Tag.objects.all()

    serializer_class = serializers.TagSerializers

    def get_queryset(self):
        """Return objects for authenticated user"""

        return self.queryset.filter(user=self.request.user).order_by('-name')

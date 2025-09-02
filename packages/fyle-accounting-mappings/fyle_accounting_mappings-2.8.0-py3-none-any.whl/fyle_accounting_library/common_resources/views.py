from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import DimensionDetail
from .serializers import DimensionDetailSerializer
from fyle_accounting_mappings.utils import (
    LookupFieldMixin,
    JSONFieldFilterBackend
)


class DimensionDetailView(LookupFieldMixin, ListAPIView):
    """
    Dimension Detail View
    """
    queryset = DimensionDetail.objects.all().order_by('-updated_at')
    serializer_class = DimensionDetailSerializer
    filter_backends = (DjangoFilterBackend, JSONFieldFilterBackend,)
    filterset_fields = {
        'attribute_type': {'exact', 'in'},
        'display_name': {'exact', 'in'},
        'source_type': {'exact', 'in'}
    }

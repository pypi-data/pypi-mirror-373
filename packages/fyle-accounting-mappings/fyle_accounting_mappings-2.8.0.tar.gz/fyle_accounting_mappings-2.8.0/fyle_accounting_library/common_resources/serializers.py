from rest_framework import serializers

from .models import DimensionDetail


class DimensionDetailSerializer(serializers.ModelSerializer):
    """
    Dimension Details Serializer
    """
    class Meta:
        model = DimensionDetail
        fields = '__all__'

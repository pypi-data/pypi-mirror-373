from django.urls import path

from .views import (
    DimensionDetailView
)


urlpatterns = [
    path('dimension_details/', DimensionDetailView.as_view(), name='dimension_details')
]

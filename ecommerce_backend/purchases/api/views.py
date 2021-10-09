from rest_framework import generics

from ecommerce_backend.purchases.api.serializers import (PersonSerializer,
                                                         SellableSerializer)
from ecommerce_backend.purchases.models import Person, Sellable


class PersonListCreateView(generics.ListCreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class SellableListCreateView(generics.ListCreateAPIView):
    queryset = Sellable.objects.prefetch_related('storable').all()
    serializer_class = SellableSerializer

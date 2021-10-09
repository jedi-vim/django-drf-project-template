from rest_framework import serializers

from ecommerce_backend.purchases.models import (Person, Purchase, Sellable,
                                                Storable)


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'username']


class SellableSerializer(serializers.ModelSerializer):
    storable = serializers.StringRelatedField()

    class Meta:
        model = Sellable
        fields = ['description', 'price', 'storable']


class StorableSerializer(serializers.ModelSerializer):
    sellable = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Storable
        fields = ['quantity_available', 'sellable']


class PurchaseSerializer(serializers.ModelSerializer):
    customer = PersonSerializer()

    class Meta:
        model = Purchase
        fields = ['status', 'created_at', 'total', 'customer', 'items']

import decimal
from datetime import datetime

import factory
from factory.django import DjangoModelFactory

from ecommerce_backend.purchases.models import (Person, Purchase, PurchaseItem,
                                                Sellable, Storable)


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person
    
    username = factory.Faker('name')
    first_name = factory.Faker('name')


class StorableFactory(DjangoModelFactory):
    class Meta:
        model = Storable

    sellable = None
    quantity_available = 10


class SellableFactory(DjangoModelFactory):
    class Meta:
        model = Sellable

    class Params:
        is_storable = factory.Trait(
            storable=factory.RelatedFactory(StorableFactory,
                                            factory_related_name='sellable')
        )

    description = factory.Sequence(lambda n: f'Sellable {n}')
    price = decimal.Decimal('1.99')
    storable = None


class PurchaseFactory(DjangoModelFactory):
    class Meta:
        model = Purchase

    class Params:
        closed = factory.Trait(
            closed_at=factory.LazyFunction(lambda: datetime.now()),
            status=Purchase.CLOSED
        )

    customer = factory.SubFactory(PersonFactory)
    salesperson = factory.SubFactory(PersonFactory)


class PurchaseItemFactory(DjangoModelFactory):
    class Meta:
        model = PurchaseItem

    purchase = factory.SubFactory(PurchaseFactory)
    sellable = factory.SubFactory(SellableFactory)
    quantity = 1

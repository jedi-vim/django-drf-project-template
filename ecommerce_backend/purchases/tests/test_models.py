import decimal

import pytest

from ecommerce_backend.purchases.exceptions import (InsufficientStockError,
                                                    PurchaseAlreadyClosed,
                                                    PurchaseItemCreateError)
from ecommerce_backend.purchases.models import Purchase, PurchaseItem
from ecommerce_backend.purchases.tests.factories import (PurchaseFactory,
                                                         SellableFactory)


@pytest.mark.django_db
def test_purchase():
    purchase = PurchaseFactory()
    purchase.save()
    assert purchase.total == decimal.Decimal(0)
    assert purchase.status == Purchase.OPENED
    assert purchase.items.count() == 0

    sellable_1 = SellableFactory(price=decimal.Decimal('1.99'),
                                 storable__quantity_available=1,
                                 is_storable=True)
    sellable_1.save()
    sellable_2 = SellableFactory(price=decimal.Decimal('2.99'))
    sellable_2.save()

    purchase.add_item(sellable_1, 1)
    purchase.add_item(sellable_2, 3)
    purchase.save()
    assert purchase.items.count() == 2
    assert purchase.total == decimal.Decimal('10.96')

    purchase.confirm()
    assert purchase.status == Purchase.CLOSED

    sellable_1.refresh_from_db()
    assert sellable_1.storable.quantity_available == 0


@pytest.mark.django_db
def test_add_to_purchase_insuficient_stock_sellable():
    purchase = PurchaseFactory()
    purchase.save()
    assert purchase.total == decimal.Decimal(0)
    assert purchase.status == Purchase.OPENED
    assert purchase.items.count() == 0

    sellable_1 = SellableFactory(price=decimal.Decimal('1.99'),
                                 storable__quantity_available=1,
                                 is_storable=True)
    sellable_1.save()

    purchase.add_item(sellable_1, 2)
    with pytest.raises(InsufficientStockError):
        purchase.confirm()

    assert purchase.status == Purchase.OPENED
    assert purchase.total == decimal.Decimal('3.98')
    sellable_1.refresh_from_db()
    assert sellable_1.storable.quantity_available == 1


@pytest.mark.django_db
def test_add_item_to_closed_purchase():
    purchase = PurchaseFactory(status=Purchase.CLOSED,
                               total=decimal.Decimal('9.99'))

    sellable_1 = SellableFactory(price=decimal.Decimal('1.00'),
                                 is_storable=True,
                                 storable__quantity_available=1,)
    with pytest.raises(PurchaseAlreadyClosed):
        purchase.add_item(sellable_1, 3)

    purchase.refresh_from_db()
    assert purchase.total == decimal.Decimal('9.99')

    sellable_1.refresh_from_db()
    assert sellable_1.storable.quantity_available == 1


@pytest.mark.django_db
def test_close_a_confirmed_purchase():
    purchase = PurchaseFactory(total=decimal.Decimal('9.99'))
    purchase.confirm()

    assert purchase.status == Purchase.CLOSED

    closed_datime = purchase.closed_at
    purchase.confirm()
    assert purchase.closed_at == closed_datime


@pytest.mark.django_db
def test_create_purchase_item():
    purchase_1 = PurchaseFactory()
    sellable_1 = SellableFactory(price=decimal.Decimal('1.50'))
    purchase_item = PurchaseItem.create(sellable=sellable_1, quantity=2,
                                        purchase=purchase_1)
    purchase_item.save()

    assert purchase_item.sellable == sellable_1
    assert purchase_item.quantity == 2
    assert purchase_item.total == decimal.Decimal('3.0')

    with pytest.raises(PurchaseItemCreateError):
        purchase_item = PurchaseItem.create(purchase=purchase_1, quantity=2)

    with pytest.raises(PurchaseItemCreateError):
        purchase_item = PurchaseItem.create(purchase=purchase_1,
                                            sellable=sellable_1)

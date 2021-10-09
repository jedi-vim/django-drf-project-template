import decimal
from datetime import datetime

import pytest
from freezegun import freeze_time

from ecommerce_backend.purchases.tests.factories import (PersonFactory,
                                                         PurchaseFactory,
                                                         PurchaseItemFactory)
from ecommerce_backend.reports.helpers import (
    sellables_acquired_ranked_by_quantity, total_comission_per_salesperson)


@pytest.mark.django_db
def test_dont_include_opened_purchases_on_salesperson_comission():
    salesperson = PersonFactory()
    salesperson.save()

    with freeze_time("2020-09-02 12:00:01"):
        purchase_1 = PurchaseFactory(total=decimal.Decimal('50.00'),
                                     salesperson=salesperson)
        purchase_1.save()

        purchase_2 = PurchaseFactory(closed=True,
                                     total=decimal.Decimal('60.00'),
                                     salesperson=salesperson)
        purchase_2.save()

    initial = datetime(2020, 9, 2, 12, 0, 0)
    end = datetime(2020, 9, 2, 12, 0, 5)
    comission_report = total_comission_per_salesperson(
        salesperson.id, initial, end)[0]

    assert comission_report['salesperson_id'] == salesperson.id
    assert comission_report['salesperson_name'] == salesperson.first_name
    assert comission_report['total_comission'] == decimal.Decimal(6)


@pytest.mark.django_db
def test_dont_include_other_salesperson_purchases_on_total_comission():
    salesperson = PersonFactory()
    salesperson.save()

    another_salesperson = PersonFactory()
    another_salesperson.save()

    with freeze_time("2020-09-02 12:00:01"):
        purchase_1 = PurchaseFactory(closed=True,
                                     total=decimal.Decimal('50.00'),
                                     salesperson=salesperson)
        purchase_1.save()

        purchase_2 = PurchaseFactory(closed=True,
                                     total=decimal.Decimal('60.00'),
                                     salesperson=another_salesperson)
        purchase_2.save()

    initial = datetime(2020, 9, 2, 12, 0, 0)
    end = datetime(2020, 9, 2, 12, 0, 5)
    comission_report = total_comission_per_salesperson(salesperson.id,
                                                       initial,
                                                       end)[0]

    assert comission_report['salesperson_id'] == salesperson.id
    assert comission_report['salesperson_name'] == salesperson.first_name
    assert comission_report['total_comission'] == decimal.Decimal(5)


@pytest.mark.django_db
def test_dont_include_purchases_out_of_datetime_interval_on_total_comission():
    salesperson = PersonFactory()
    salesperson.save()

    with freeze_time("2020-09-02 12:00:01"):
        purchase_1 = PurchaseFactory(closed=True,
                                     total=decimal.Decimal('50.00'),
                                     salesperson=salesperson)
        purchase_1.save()

    with freeze_time("2020-09-02 12:00:06"):
        purchase_2 = PurchaseFactory(closed=True,
                                     total=decimal.Decimal('60.00'),
                                     salesperson=salesperson)
        purchase_2.save()

    initial = datetime(2020, 9, 2, 12, 0, 0)
    end = datetime(2020, 9, 2, 12, 0, 5)
    comission_report = total_comission_per_salesperson(salesperson.id,
                                                       initial, end)[0]
    assert comission_report['salesperson_id'] == salesperson.id
    assert comission_report['salesperson_name'] == salesperson.first_name
    assert comission_report['total_comission'] == decimal.Decimal(5)


@pytest.mark.django_db
def test_acquired_sellables_exclude_another_customers_purchase_items():

    customer_1 = PersonFactory()
    customer_1.save()
    with freeze_time("2020-09-02 12:00:01"):
        item_1 = PurchaseItemFactory(sellable__description='sellable_1',
                                     sellable__price=decimal.Decimal('1.99'),
                                     purchase__customer=customer_1,
                                     purchase__closed=True, quantity=2)
        item_1.save()
        item_2 = PurchaseItemFactory(sellable__description='sellable_2',
                                     sellable__price=decimal.Decimal('2.99'),
                                     purchase__customer=customer_1,
                                     purchase__closed=True, quantity=3)
        item_2.save()
        item_3 = PurchaseItemFactory(sellable__description='sellable_3',
                                     sellable__price=decimal.Decimal('3.99'),
                                     purchase__customer=None,
                                     purchase__closed=True)
        item_3.save()

    initial = datetime(2020, 9, 2, 12, 0, 0)
    end = datetime(2020, 9, 2, 12, 0, 5)
    sellables_acquired = sellables_acquired_ranked_by_quantity(
        initial, end, customer_id=customer_1.id)
    assert sellables_acquired[0] == {
        'sellable_id': item_1.sellable.id,
        'sellable_description': 'sellable_1',
        'total_purchased': 2
    }
    assert sellables_acquired[1] == {
        'sellable_id': item_2.sellable.id,
        'sellable_description': 'sellable_2',
        'total_purchased': 3
    }


@pytest.mark.django_db
def test_acquired_sellables_exclude_items_from_not_closed_purchases():
    customer_1 = PersonFactory()
    customer_1.save()
    with freeze_time("2020-09-02 12:00:01"):
        item_1 = PurchaseItemFactory(sellable__description='sellable_1',
                                     sellable__price=decimal.Decimal('1.99'),
                                     purchase__customer=customer_1,
                                     purchase__closed=True, quantity=2)
        item_1.save()
        item_2 = PurchaseItemFactory(sellable=item_1.sellable,
                                     purchase__customer=customer_1,
                                     quantity=3)
        item_2.save()
        item_3 = PurchaseItemFactory(sellable=item_1.sellable,
                                     purchase__customer=customer_1,
                                     purchase__closed=True,
                                     quantity=4)
        item_3.save()

    initial = datetime(2020, 9, 2, 12, 0, 0)
    end = datetime(2020, 9, 2, 12, 0, 5)
    sellables_acquired = sellables_acquired_ranked_by_quantity(initial,
                                                               end,
                                                               customer_1.id)
    assert sellables_acquired[0] == {
        'sellable_id': item_1.sellable.id,
        'sellable_description': 'sellable_1',
        'total_purchased': 6
    }


@pytest.mark.django_db
def test_acquired_sellables_exclude_purchases_out_of_datetime_interval():
    customer_1 = PersonFactory()
    customer_1.save()

    with freeze_time("2020-09-02 12:00:01"):
        item_1 = PurchaseItemFactory(sellable__description='sellable_1',
                                     sellable__price=decimal.Decimal('1.99'),
                                     purchase__customer=customer_1,
                                     purchase__closed=True, quantity=1)
        item_1.save()

    with freeze_time("2020-09-02 12:00:05"):
        item_2 = PurchaseItemFactory(sellable=item_1.sellable,
                                     purchase__customer=customer_1,
                                     purchase__closed=True,
                                     quantity=2)
        item_2.save()

    with freeze_time("2020-09-02 12:00:07"):
        item_3 = PurchaseItemFactory(sellable=item_1.sellable,
                                     purchase__customer=customer_1,
                                     purchase__closed=True,
                                     quantity=3)
        item_3.save()

    initial = datetime(2020, 9, 2, 12, 0, 0)
    end = datetime(2020, 9, 2, 12, 0, 5)
    sellables_acquired = sellables_acquired_ranked_by_quantity(initial,
                                                               end,
                                                               customer_1.id)
    assert sellables_acquired[0] == {
        'sellable_id': item_1.sellable.id,
        'sellable_description': 'sellable_1',
        'total_purchased': 3
    }

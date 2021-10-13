import decimal

import pytest
from django.urls import reverse
from freezegun import freeze_time

from ecommerce_backend.purchases.tests.factories import (
    PersonFactory,
    PurchaseFactory,
    PurchaseItemFactory,
)


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize(
    "params,response_code,response_body",
    [
        (
            {
                "salesperson_id": 1,
                "begin": "2020-09-02 12:00:00",
                "end": "2020-09-02 12:00:05",
            },
            200,
            {
                "salesperson_id": 1,
                "salesperson_name": "Leonam",
                "total_comission": "11.00",
            },
        ),
        (
            {
                "salesperson_id": 99,
                "begin": "2020-09-02 12:00:00",
                "end": "2020-09-02 12:00:05",
            },
            404,
            {"detail": "Report not available"},
        ),
        ({}, 400, {"salesperson_id": "Salesperson ID not provided"}),
        (
            {"salesperson_id": "wrongID"},
            400,
            {"salesperson_id": "wrongID is a invalid ID"},
        ),
    ],
)
def test_get_commission_per_salesperson(app, params, response_code, response_body):
    salesperson = PersonFactory(first_name="Leonam")
    salesperson.save()

    with freeze_time("2020-09-02 12:00:01"):
        purchase_1 = PurchaseFactory(
            total=decimal.Decimal("50.00"), closed=True, salesperson=salesperson
        )
        purchase_1.save()

        purchase_2 = PurchaseFactory(
            closed=True, total=decimal.Decimal("60.00"), salesperson=salesperson
        )
        purchase_2.save()

    response = app.get(reverse("reports:comission_per_salesperson"), params)
    assert response.status_code == response_code
    assert response.json() == response_body


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.parametrize(
    "params,response_code,response_body",
    [
        (
            {
                "customer_id": 1,
                "begin": "2020-09-02 12:00:00",
                "end": "2020-09-02 12:00:05",
            },
            200,
            [
                {
                    "sellable_description": "sellable_1",
                    "sellable_id": 1,
                    "total_purchased": "2.00",
                },
                {
                    "sellable_description": "sellable_2",
                    "sellable_id": 2,
                    "total_purchased": "3.00",
                },
            ],
        ),
        (
            {
                "customer_id": 2,
                "begin": "2020-09-02 12:00:00",
                "end": "2020-09-02 12:00:05",
            },
            200,
            [
                {
                    "sellable_description": "sellable_4",
                    "sellable_id": 4,
                    "total_purchased": "2.00",
                },
            ],
        ),
        (
            {
                "customer_id": 1,
                "begin": "2020-09-02 12:00:06",
                "end": "2020-09-02 12:00:07",
            },
            404,
            {"detail": "Report not available"},
        ),
        (
            {"begin": "2020-09-02 12:00:00", "end": "2020-09-02 12:00:05"},
            200,
            [
                {
                    "sellable_description": "sellable_1",
                    "sellable_id": 1,
                    "total_purchased": "2.00",
                },
                {
                    "sellable_description": "sellable_2",
                    "sellable_id": 2,
                    "total_purchased": "3.00",
                },
                {
                    "sellable_description": "sellable_3",
                    "sellable_id": 3,
                    "total_purchased": "1.00",
                },
                {
                    "sellable_description": "sellable_4",
                    "sellable_id": 4,
                    "total_purchased": "2.00",
                },
            ],
        ),
    ],
)
def test_get_sellable_purchased_by_consumer(app, params, response_code, response_body):
    customer_1 = PersonFactory()
    customer_1.save()

    customer_2 = PersonFactory()
    customer_2.save()

    with freeze_time("2020-09-02 12:00:01"):
        item_1 = PurchaseItemFactory(
            sellable__description="sellable_1",
            sellable__price=decimal.Decimal("1.99"),
            purchase__customer=customer_1,
            purchase__closed=True,
            quantity=2,
        )
        item_1.save()

        item_2 = PurchaseItemFactory(
            sellable__description="sellable_2",
            sellable__price=decimal.Decimal("2.99"),
            purchase__customer=customer_1,
            purchase__closed=True,
            quantity=3,
        )
        item_2.save()

        item_3 = PurchaseItemFactory(
            sellable__description="sellable_3",
            sellable__price=decimal.Decimal("3.99"),
            purchase__customer=None,
            purchase__closed=True,
        )
        item_3.save()

        item_4 = PurchaseItemFactory(
            sellable__description="sellable_4",
            sellable__price=decimal.Decimal("1.99"),
            purchase__customer=customer_2,
            purchase__closed=True,
            quantity=2,
        )
        item_4.save()

        item_5 = PurchaseItemFactory(
            sellable=item_1.sellable, purchase__customer=customer_2, quantity=3
        )
        item_5.save()

    response = app.get(reverse("reports:sellables_ranking"), params)
    assert response.status_code == response_code
    assert response.json() == response_body

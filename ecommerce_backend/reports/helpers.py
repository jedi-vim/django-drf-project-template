from django.db.models import F, Q
from django.db.models.aggregates import Sum
from django.db.models.functions import Concat

from ecommerce_backend.purchases.models import Purchase, PurchaseItem


def total_comission_per_salesperson(salesperson_id, initial, end):
    return (
        Purchase.objects.filter(
            Q(salesperson__id=salesperson_id)
            & Q(status=Purchase.CLOSED)
            & Q(closed_at__gte=initial)
            & Q(closed_at__lte=end)
        )
        .values(
            "salesperson_id",
            salesperson_name=Concat(F("salesperson__first_name"), F("salesperson__last_name")),
        )
        .annotate(total_comission=(Sum("total") / 10))
    )


def sellables_acquired_ranked_by_quantity(initial=None, end=None, customer_id=None):
    criteria = (
        Q(purchase__status=Purchase.CLOSED) & Q(purchase__closed_at__gte=initial) & Q(purchase__closed_at__lte=end)
    )
    if customer_id:
        criteria = criteria & Q(purchase__customer__id=customer_id)
    return (
        PurchaseItem.objects.filter(criteria)
        .values("sellable_id", sellable_description=F("sellable__description"))
        .annotate(total_purchased=Sum("quantity"))
        .all()
    )

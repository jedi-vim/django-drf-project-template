from django.urls import path

from ecommerce_backend.reports.api.views import (CommisionPerSalespersonView,
                                                 SellablePurchasedRankingView)

app_name = 'reports'
urlpatterns = [
    path(
        'comissions/',
        CommisionPerSalespersonView.as_view(),
        name='comission_per_salesperson'),
    path(
        'sellables_ranking/',
        SellablePurchasedRankingView.as_view(),
        name='sellables_ranking'),
]

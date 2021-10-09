from django.urls import path

from ecommerce_backend.purchases.api.views import (PersonListCreateView,
                                                   SellableListCreateView)

app_name = 'purchases'
urlpatterns = [
        path('persons/', PersonListCreateView.as_view(), name='persons'),
        path('sellables/', SellableListCreateView.as_view(), name='sellables'),
]

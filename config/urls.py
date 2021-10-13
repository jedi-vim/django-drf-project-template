from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('ecommerce_backend.purchases.urls',
                     namespace='purchases')),
    path('reports', include('ecommerce_backend.reports.urls',
                            namespace='reports')),
]

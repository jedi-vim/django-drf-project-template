from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from .exceptions import (InsufficientStockError, PurchaseAlreadyClosed,
                         PurchaseItemCreateError)


class Person(User):
    pass


class Sellable(models.Model):
    description = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=9, decimal_places=2, null=False)


class Storable(models.Model):
    sellable = models.OneToOneField(Sellable, on_delete=models.CASCADE,
                                    null=True, related_name='storable')
    quantity_available = models.IntegerField(default=0)

    def decrease(self, quantity: int):
        if quantity > self.quantity_available:
            sellable_name = self.sellable.description
            raise InsufficientStockError(f'Sellable {sellable_name} canno\'t be decreased by {quantity}')
        self.quantity_available -= quantity

    def increase(self, quantity: int):
        self.quantity_available += quantity

    def __str__(self):
        return f'Storable {self.id} - {self.quantity_available} in stock'


class Purchase(models.Model):
    OPENED = 'opened'
    CLOSED = 'closed'
    STATUSES = [
        (OPENED, 'opened'),
        (CLOSED, 'closed'),
    ]
    status = models.CharField(default=OPENED, max_length=15,
                              choices=STATUSES)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True)
    customer = models.ForeignKey(Person, on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='customer_purchases')
    salesperson = models.ForeignKey(Person, on_delete=models.SET_NULL,
                                    null=True,
                                    related_name='salesperson_purchases')
    total = models.DecimalField(max_digits=9, decimal_places=2,
                                default=Decimal(0))

    def add_item(self, sellable: Sellable, quantity: int):
        if self.status == Purchase.CLOSED:
            raise PurchaseAlreadyClosed(f'Purchase {self.id} canno\'t accept new items')
        
        item = PurchaseItem.create(purchase=self, sellable=sellable,
                                   quantity=quantity)
        item.save()
        self.total = self.total + item.total

    def confirm(self):
        if self.status == Purchase.CLOSED:
            return 
        for item in self.items.all():
            item.confirm()
        self.closed_at = datetime.now()
        self.status = Purchase.CLOSED
        self.save()

    @property
    def total_comission(self) -> Decimal:
        return self.total / 10


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE,
                                 related_name='items')
    sellable = models.ForeignKey(Sellable, on_delete=models.SET_NULL,
                                 null=True)
    quantity = models.IntegerField(null=False)
    total = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    @classmethod
    def create(cls, *args, **kwargs):
        if not kwargs.get('quantity', None):
            raise PurchaseItemCreateError('Missing quantity')
        if not kwargs.get('sellable', None):
            raise PurchaseItemCreateError('Missing sellable')
        sellable, quantity = kwargs['sellable'], kwargs['quantity']
        total = sellable.price * quantity
        kwargs['total'] = total
        return cls(*args, **kwargs)

    def confirm(self):
        storable = getattr(self.sellable, 'storable', None)
        if not storable:
            return
        storable.decrease(self.quantity)
        storable.save()

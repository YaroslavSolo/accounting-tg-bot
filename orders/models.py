from django.db import models
from tgusers.models import User
from products.models import Product


# Create your models here.
class Order(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    completed_time = models.DateTimeField(null=True)
    deadline_time = models.DateTimeField(null=True)
    order_sum = models.PositiveIntegerField(null=False)

    CREATED = 'CR'
    COMPLETED = 'CO'

    ORDER_STATUS_CHOICES = [
        (CREATED, 'CREATED'),
        (COMPLETED, 'COMPLETED'),
    ]

    status = models.CharField(max_length=2, choices=ORDER_STATUS_CHOICES)

    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, db_index=True)


class OrderProducts(models.Model):
    order_id = models.ForeignKey(to=Order, on_delete=models.CASCADE, db_index=True)
    product_id = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=False)

from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(primary_key=True, null=False)
    username = models.CharField(default='', max_length=32, blank=True, null=False)
    products_count = models.PositiveIntegerField(default=0, null=False)
    orders_count = models.PositiveIntegerField(default=0, null=False)
    materials_count = models.PositiveIntegerField(default=0, null=False)
    notifications_enabled = models.BooleanField(default=True, null=False)

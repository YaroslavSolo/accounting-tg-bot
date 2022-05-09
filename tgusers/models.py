from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(primary_key=True, null=False)
    products_count = models.IntegerField(default=0, null=False)
    orders_count = models.IntegerField(default=0, null=False)

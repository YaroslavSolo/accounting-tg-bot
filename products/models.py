from django.db import models


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=False)
    price = models.IntegerField(default=0)

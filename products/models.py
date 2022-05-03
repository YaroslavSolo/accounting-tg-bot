from django.db import models
from tgusers.models import User


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=64, null=False)
    description = models.TextField(blank=True, null=False, max_length=300)
    price = models.IntegerField(default=0)  # in rubles
    production_time = models.PositiveIntegerField(default=0)  # in days
    amount = models.PositiveIntegerField(default=0, null=False)

    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, db_index=True)

from django.db import models
from tgusers.models import User


class Product(models.Model):
    name = models.CharField(max_length=64, blank=False, null=False, unique=True)
    description = models.CharField(max_length=250, blank=True, null=False)
    price = models.PositiveIntegerField(default=0)  # in rubles
    production_time = models.PositiveIntegerField(default=0)  # in days
    amount = models.PositiveIntegerField(default=0, null=False)

    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return f'📦  *{self.name}*\n' \
               f'{self.description}\n' \
               f'Цена: {self.price} руб.\n' \
               f'Время изготовления: {self.production_time} (дни)\n' \
               f'Количество товара: {self.amount}'

    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'name']),
        ]

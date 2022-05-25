from django.db import models
from tgusers.models import User


class Material(models.Model):
    name = models.CharField(max_length=64, blank=False, null=False, unique=True)
    price = models.PositiveIntegerField(default=0)  # in rubles
    amount = models.PositiveIntegerField(default=0, null=False)  # in standard units

    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return f'🧱 *{self.name}*\n' \
               f'Цена: {self.price} руб.\n' \
               f'Количество: {self.amount} у.е.'

    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'name']),
        ]

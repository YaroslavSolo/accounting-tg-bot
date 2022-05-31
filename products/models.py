from django.db import models

from tgusers.models import User
from materials.models import Material


class Product(models.Model):
    name = models.CharField(max_length=64, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True, null=False)
    price = models.PositiveIntegerField(default=0)  # in rubles
    production_time = models.PositiveIntegerField(default=0)  # in days
    amount = models.IntegerField(default=0, null=False)

    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, db_index=True)

    def get_materials_str(self):
        product_materials = ProductMaterials.objects.filter(product=self)
        result = ''
        for material in product_materials:
            result += f'{str(material)}\n'

        return result

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        product_count_str = f'0 ({-self.amount} необходимо изготовить)' if self.amount < 0 else f'{self.amount}'
        return f'📦 *{self.name}*\n' \
               f'{self.description}\n' \
               f'Цена: {self.price} руб.\n' \
               f'Время изготовления: {self.production_time} (дни)\n' \
               f'Количество товара: {product_count_str}\n' \
               f'{self.get_materials_str()}'

    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'name']),
        ]


class ProductMaterials(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, db_index=True)
    material = models.ForeignKey(to=Material, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=False)

    def __str__(self):
        return f'🧱  *{self.material.name}* - {self.amount}x'

from django.db import models

from tgusers.models import User
from products.models import Product


class Order(models.Model):
    description = models.TextField(blank=False, null=False, max_length=250)
    created_time = models.DateTimeField(auto_now_add=True)
    completed_time = models.DateTimeField(null=True)
    deadline_time = models.DateTimeField(null=False)
    order_sum = models.PositiveIntegerField(default=0, null=False)

    CREATED = 'CR'
    COMPLETED = 'CO'

    ORDER_STATUS_CHOICES = [
        (CREATED, 'CREATED'),
        (COMPLETED, 'COMPLETED'),
    ]

    ORDER_STATUS_RUS = {
        CREATED: 'создан',
        COMPLETED: 'завершен'
    }

    status = models.CharField(max_length=2, choices=ORDER_STATUS_CHOICES, default=CREATED)

    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, db_index=True)

    def get_products_str(self):
        order_products = OrderProducts.objects.filter(order=self)
        result = ''
        for order_product in order_products:
            result += f'{str(order_product)}\n'

        return result

    def __str__(self):
        deadline = self.deadline_time.strftime('%d.%m.%Y %H:%M')
        return f'📃  *{self.description}*\n' \
               f'Дедлайн: {deadline}\n' \
               f'Сумма заказа: {self.order_sum} руб.\n' \
               f'Статус: {self.ORDER_STATUS_RUS[self.status]}\n' \
               f'{self.get_products_str()}'


class OrderProducts(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, db_index=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=False)

    def __str__(self):
        return f'📦  *{self.product.name}* - {self.amount}x'

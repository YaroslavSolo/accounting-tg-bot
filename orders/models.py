from django.db import models

from tgusers.models import User
from products.models import Product


class Order(models.Model):
    description = models.CharField(max_length=250, blank=False, null=False)
    created_time = models.DateTimeField(auto_now_add=True, null=False)
    completed_time = models.DateTimeField(null=True)
    deadline_time = models.DateTimeField(null=False)
    order_sum = models.PositiveIntegerField(default=0, null=False)
    num_products = models.PositiveIntegerField(default=0, null=False)

    CREATED = 'CR'
    COMPLETED_IN_TIME = 'CO'
    COMPLETED_WITH_DELAY = 'COWD'

    ORDER_STATUS_CHOICES = [
        (CREATED, 'CREATED'),
        (COMPLETED_IN_TIME, 'COMPLETED_IN_TIME'),
        (COMPLETED_WITH_DELAY, 'COMPLETED_WITH_DELAY')
    ]

    ORDER_STATUS_RUS = {
        CREATED: 'создан',
        COMPLETED_IN_TIME: 'завершен вовремя',
        COMPLETED_WITH_DELAY: 'завершен с опозданием'
    }

    status = models.CharField(max_length=4, choices=ORDER_STATUS_CHOICES, default=CREATED)

    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE, db_index=True)

    def is_completed(self):
        return self.status == Order.COMPLETED_IN_TIME or self.status == Order.COMPLETED_WITH_DELAY

    def get_products_str(self):
        order_products = OrderProducts.objects.filter(order=self)
        result = ''
        for order_product in order_products:
            result += f'{str(order_product)}\n'

        return result

    def __str__(self):
        deadline = self.deadline_time.strftime('%d.%m.%Y %H:%M')
        return f'📃 Заказ № *{self.id}*\n' \
               f'*{self.description}*\n' \
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

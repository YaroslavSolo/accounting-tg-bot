from asgiref.sync import sync_to_async

from .models import Order, OrderProducts
from tgusers.models import User


ORDER_LIMIT = 4


@sync_to_async
def save_order(raw_order, user_id):
    user = User.objects.get(telegram_id=user_id)
    user.orders_count += 1
    user.save()

    deadline_time = raw_order['deadline_date']
    deadline_time = deadline_time.replace(hour=raw_order['deadline_time'].hour, minute=raw_order['deadline_time'].minute)

    order = Order(
        description=raw_order['description'],
        deadline_time=deadline_time,
        user_id=user
    )
    order.save()
    return order


@sync_to_async
def get_active_orders_str(user_id, offset, limit=ORDER_LIMIT):
    result = ''
    orders = Order.objects.filter(user_id=user_id).order_by('created_time')[offset:offset + limit]
    for order in orders:
        result += str(order) + '\n'

    return result


@sync_to_async
def get_active_orders_count(user_id):
    return Order.objects.filter(user_id=user_id).count()


@sync_to_async
def save_order_products(order, product, amount):
    order.order_sum += product.price * amount
    order.save()
    order_products = OrderProducts(order=order, product=product, amount=amount)
    order_products.save()


@sync_to_async
def clear_orders(user_id):
    Order.objects.filter(user_id=user_id).delete()

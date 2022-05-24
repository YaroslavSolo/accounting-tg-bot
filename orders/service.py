from asgiref.sync import sync_to_async
from django.db import transaction
from .models import Order, OrderProducts
from tgusers.models import User


ORDER_LIMIT = 4


@sync_to_async
@transaction.atomic
def save_order(raw_order, user_id):
    user = User.objects.get(telegram_id=user_id)
    user.orders_count += 1
    user.save()

    deadline_time = raw_order['deadline_date']
    deadline_time = deadline_time.replace(
        hour=raw_order['deadline_time'].hour,
        minute=raw_order['deadline_time'].minute
    )

    order = Order(
        description=raw_order['description'],
        deadline_time=deadline_time,
        user_id=user,
    )
    order.save()
    return order


@sync_to_async
def get_order(user_id, order_id):
    return Order.objects.filter(id=order_id, user_id=user_id).first()


@sync_to_async
def get_order_str(user_id, order_id):
    return str(Order.objects.filter(id=order_id, user_id=user_id).first())


@sync_to_async
def get_order_exists(user_id, order_id):
    return Order.objects.filter(id=order_id, user_id=user_id).first() is not None


@sync_to_async
def get_active_orders_str(user_id, offset, limit=ORDER_LIMIT):
    result = ''
    orders = Order.objects.filter(user_id=user_id).order_by('created_time')[offset:offset + limit]
    for order in orders:
        result += str(order) + '\n'

    return result


@sync_to_async
def get_products_for_orders(order_ids):
    return list(OrderProducts.objects.filter(order__in=order_ids).values('product', 'amount'))


@sync_to_async
def get_active_orders_count(user_id):
    return Order.objects.filter(user_id=user_id).count()


@sync_to_async
def get_completed_orders_between(user_id, period_start, period_end):
    return Order.objects.all()
    # return Order.objects.filter(
    #     user_id=user_id,
    #     completed_time__isnull=False,
    #     completed_time__gte=period_start,
    #     completed_time__lte=period_end
    # )


@sync_to_async
@transaction.atomic
def save_order_products(order, product, amount):
    order.order_sum += product.price * amount
    order.num_products += amount
    order.save()
    order_products = OrderProducts(order=order, product=product, amount=amount)
    order_products.save()


@sync_to_async
@transaction.atomic
def delete_order(user_id, order_id):
    num, _ = Order.objects.filter(id=order_id, user_id=user_id).delete()
    user = User.objects.filter(telegram_id=user_id).first()
    user.orders_count -= num
    user.save()


@sync_to_async
@transaction.atomic
def clear_orders(user_id):
    user = User.objects.filter(telegram_id=user_id).first()
    user.orders_count = 0
    user.save()
    Order.objects.filter(user_id=user_id).delete()

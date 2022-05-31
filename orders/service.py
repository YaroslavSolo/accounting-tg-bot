from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from django.db import transaction
from .models import Order, OrderProducts
from tgusers.models import User
from materials.service import get_materials
from products.models import ProductMaterials, Product


ORDER_LIMIT = 3


@sync_to_async
@transaction.atomic
def save_order(raw_order, user_id):
    user = User.objects.get(telegram_id=user_id)
    user.orders_count += 1
    user.save()

    deadline_time = raw_order['deadline_date']
    deadline_time = deadline_time.replace(
        hour=raw_order['deadline_time'].hour,
        minute=raw_order['deadline_time'].minute,
        tzinfo=timezone.utc
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
def get_orders_str(user_id, offset, limit=ORDER_LIMIT):
    result = ''
    orders = Order.objects.filter(user_id=user_id).order_by('deadline_time')[offset:offset + limit]
    for order in orders:
        result += str(order) + '\n'

    return result


@sync_to_async
def get_products_for_orders(order_ids):
    return list(OrderProducts.objects.filter(order__in=order_ids).values('product', 'amount'))


@sync_to_async
def get_orders_count(user_id):
    return Order.objects.filter(user_id=user_id).count()


@sync_to_async
def get_completed_orders_between(user_id, period_start, period_end):
    return Order.objects.filter(
        user_id=user_id,
        completed_time__isnull=False,
        completed_time__gte=period_start,
        completed_time__lte=period_end
    )


@sync_to_async
def get_created_orders_count(user_id, period_start, period_end):
    return Order.objects.filter(
        user_id=user_id,
        created_time__gte=period_start,
        created_time__lte=period_end
    ).count()


@sync_to_async
@transaction.atomic
def save_order_products(order, product, amount):
    order.order_sum += product.price * amount
    order.num_products += amount
    order.save()
    order_products = OrderProducts(order=order, product=product, amount=amount)
    order_products.save()


@sync_to_async
def get_insufficient_products(order):
    order_products = OrderProducts.objects.filter(order=order)
    count_by_product = {product: 0 for product in Product.objects.filter(user_id=order.user_id)}
    insufficient_products = {}

    for order_product in order_products:
        count_by_product[order_product.product] += order_product.amount

    for product in count_by_product:
        if count_by_product[product] > 0:
            if product.amount <= 0:
                insufficient_products[product] = count_by_product[product]
            elif count_by_product[product] > product.amount:
                insufficient_products[product] = count_by_product[product] - product.amount
            product.amount -= count_by_product[product]

    for product in count_by_product.keys():
        product.save()
    return insufficient_products


@sync_to_async
def get_insufficient_materials(order, insufficient_products):
    if not insufficient_products:
        return []

    count_by_material = {material: 0 for material in get_materials(order.user_id)}
    insufficient_materials_pairs = []

    for product in insufficient_products:
        product_materials = ProductMaterials.objects.filter(product=product)
        for product_material in product_materials:
            count_by_material[product_material.material] += insufficient_products[product] * product_material.amount

    for material in count_by_material:
        if count_by_material[material] > 0:
            if material.amount <= 0:
                insufficient_materials_pairs.append((material.name, count_by_material[material]))
            elif count_by_material[material] > material.amount:
                insufficient_materials_pairs.append((material.name, count_by_material[material] - material.amount))

    return insufficient_materials_pairs


@sync_to_async
def finish_order(user_id, order_id):
    order = Order.objects.filter(id=order_id, user_id=user_id).first()
    if order is not None and not order.is_completed() and not order.is_cancelled():
        order.completed_time = datetime.now().replace(tzinfo=timezone.utc)
        if order.deadline_time.replace(tzinfo=timezone.utc) >= order.completed_time:
            order.status = Order.COMPLETED_IN_TIME
        else:
            order.status = Order.COMPLETED_WITH_DELAY

        order.save()


@sync_to_async
@transaction.atomic
def cancel_order(user_id, order_id):
    order = Order.objects.filter(id=order_id, user_id=user_id).first()
    if order is None or order.is_cancelled():
        return

    order.status = Order.CANCELLED
    order.save()
    order_products = OrderProducts.objects.filter(order=order)
    for order_product in order_products:
        order_product.product.amount += order_product.amount
        order_product.product.save()


@sync_to_async
@transaction.atomic
def delete_order(user_id, order_id):
    Order.objects.filter(id=order_id, user_id=user_id).delete()
    user = User.objects.filter(telegram_id=user_id).first()
    user.orders_count -= 1
    user.save()


@sync_to_async
@transaction.atomic
def clear_orders(user_id):
    user = User.objects.filter(telegram_id=user_id).first()
    user.orders_count = 0
    user.save()
    Order.objects.filter(user_id=user_id).delete()

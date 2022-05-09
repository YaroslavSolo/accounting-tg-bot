from asgiref.sync import sync_to_async

from tgusers.models import User
from .models import Product


PRODUCT_LIMIT = 4
PRODUCT_NAMES_LIMIT = 6


@sync_to_async
def save_product(raw_product, user_id):
    user = User.objects.get(telegram_id=user_id)
    user.products_count += 1
    user.save()

    product = Product(
        name=raw_product['name'],
        description=raw_product['description'],
        price=raw_product['price'],
        production_time=raw_product['production_time'],
        user_id=user
    )
    product.save()


@sync_to_async
def get_product(user_id, name):
    product_qs = Product.objects.filter(user_id=user_id, name=name)
    if len(product_qs) == 0:
        return None
    return product_qs[0]


@sync_to_async
def get_products_str(user_id, offset, limit=PRODUCT_LIMIT):
    result = ''
    products = Product.objects.filter(user_id=user_id).order_by('name')[offset:offset + limit]
    for product in products:
        result += str(product) + '\n\n'

    return result


@sync_to_async
def get_product_names(user_id, offset, limit=PRODUCT_NAMES_LIMIT):
    return list(Product.objects.filter(user_id=user_id).order_by('name').values_list('name', flat=True)[offset:offset + limit])


@sync_to_async
def get_products_count(user_id):
    return Product.objects.filter(user_id=user_id).count()


@sync_to_async
def delete_product(user_id, name):
    Product.objects.filter(user_id=user_id, name=name).delete()


@sync_to_async
def clear_products(user_id):
    Product.objects.filter(user_id=user_id).delete()
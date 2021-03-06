from asgiref.sync import sync_to_async
from django.db import transaction
from tgusers.models import User
from .models import Product, ProductMaterials


PRODUCT_LIMIT = 3
PRODUCT_NAMES_LIMIT = 6


@sync_to_async
@transaction.atomic
def save_product(raw_product, user_id):
    user = User.objects.get(telegram_id=user_id)
    user.products_count += 1
    user.save()

    Product(
        name=raw_product['name'],
        description=raw_product['description'],
        price=raw_product['price'],
        production_time=raw_product['production_time'],
        amount=raw_product['amount'],
        user_id=user
    ).save()


@sync_to_async
def save_product_materials(product, material, amount):
    ProductMaterials(
        product=product,
        material=material,
        amount=amount
    ).save()


@sync_to_async
def get_product(user_id, name):
    return Product.objects.filter(user_id=user_id, name=name).first()


@sync_to_async
def get_product_str(user_id, name):
    return str(Product.objects.filter(user_id=user_id, name=name).first())


@sync_to_async
def get_products_str(user_id, offset, limit=PRODUCT_LIMIT):
    result = ''
    products = Product.objects.filter(user_id=user_id).order_by('name')[offset:offset + limit]
    for product in products:
        result += str(product) + '\n'

    return result


@sync_to_async
def get_product_names_and_ids(user_id, offset, limit=PRODUCT_NAMES_LIMIT):
    return list(Product.objects.filter(user_id=user_id).order_by('name').values_list('name', flat=True)[offset:offset + limit])


@sync_to_async
def get_product_ids_and_names(user_id):
    return list(Product.objects.filter(user_id=user_id).order_by('name').values_list('id', 'name'))


@sync_to_async
def get_products_count(user_id):
    return User.objects.filter(telegram_id=user_id).first().products_count


@sync_to_async
@transaction.atomic
def delete_product(user_id, name):
    Product.objects.filter(user_id=user_id, name=name).delete()
    user = User.objects.filter(telegram_id=user_id).first()
    user.products_count -= 1
    user.save()


@sync_to_async
def clear_materials(user_id, name):
    product = Product.objects.filter(user_id=user_id, name=name).first()
    ProductMaterials.objects.filter(product=product).delete()


@sync_to_async
@transaction.atomic
def clear_products(user_id):
    user = User.objects.filter(telegram_id=user_id).first()
    user.products_count = 0
    user.save()
    Product.objects.filter(user_id=user_id).delete()

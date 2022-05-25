from asgiref.sync import sync_to_async
from django.db import transaction
from tgusers.models import User
from .models import Material


MATERIAL_LIMIT = 4
MATERIAL_NAMES_LIMIT = 8


@sync_to_async
@transaction.atomic
def save_material(raw_material, user_id):
    user = User.objects.get(telegram_id=user_id)
    user.materials_count += 1
    user.save()

    material = Material(
        name=raw_material['name'],
        price=raw_material['price'],
        amount=raw_material['amount'],
        user_id=user
    )
    material.save()


@sync_to_async
def get_material(user_id, name):
    return Material.objects.filter(user_id=user_id, name=name).first()


@sync_to_async
def get_materials_str(user_id, offset, limit=MATERIAL_LIMIT):
    result = ''
    materials = Material.objects.filter(user_id=user_id).order_by('name')[offset:offset + limit]
    for material in materials:
        result += str(material) + '\n\n'

    return result


@sync_to_async
def get_material_names(user_id, offset, limit=MATERIAL_NAMES_LIMIT):
    return list(Material.objects.filter(user_id=user_id).order_by('name').values_list('name', flat=True)[offset:offset + limit])


@sync_to_async
def get_materials_count(user_id):
    return User.objects.filter(telegram_id=user_id).first().materials_count


@sync_to_async
@transaction.atomic
def delete_material(user_id, name):
    num, _ = Material.objects.filter(user_id=user_id, name=name).delete()
    user = User.objects.filter(telegram_id=user_id).first()
    user.materials_count -= num
    user.save()


@sync_to_async
@transaction.atomic
def clear_materials(user_id):
    user = User.objects.filter(telegram_id=user_id).first()
    user.materials_count = 0
    user.save()
    Material.objects.filter(user_id=user_id).delete()

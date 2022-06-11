from datetime import datetime, timezone
from datetime import timedelta
from asgiref.sync import sync_to_async

from .models import DeadlineNotification
from tgusers.models import User


@sync_to_async
def get_notifications_count():
    return DeadlineNotification.objects.count()


@sync_to_async
def process_notifications_batch(offset, batch_size):
    result = []
    batch = DeadlineNotification.objects.all()[offset:offset + batch_size]
    for notification in batch:
        now_plus_offset = datetime.now() + timedelta(hours=5)
        now_plus_offset = now_plus_offset.replace(tzinfo=timezone.utc)
        if now_plus_offset > notification.order.deadline_time and notification.user_id.notifications_enabled:
            result.append((notification.user_id.telegram_id, notification.order.id))
            notification.delete()

    return result


@sync_to_async
def save_notification(order):
    notification = DeadlineNotification(
        order=order,
        user_id=order.user_id
    )
    notification.save()


@sync_to_async
def save_notification_if_not_exists(order):
    if DeadlineNotification.objects.filter(order=order).count() == 0:
        notification = DeadlineNotification(
            order=order,
            user_id=order.user_id
        )
        notification.save()

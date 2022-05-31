from django.db import models
from tgusers.models import User
from orders.models import Order


class DeadlineNotification(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE)

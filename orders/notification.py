from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order,Notification

@receiver(post_save, sender = Order)
def order_notification(sender,instance,created,**kwargs):
    if created:
        Notification.objects.create(
            user = instance.buyer,
            order = instance,
            message = f"your order {instance.id} has been placed"
        )
        Notification.objects.create(
            user = instance.service.seller,
            order = instance,
            message = f"New Order palced on {instance.service.title}"
        )
    else:
        Notification.objects.create(
            user = instance.buyer,
            order = instance,
            message = f"your order status changed to {instance.status}"
        )
        Notification.objects.create(
            user = instance.service.seller,
            order = instance,
            message = f"Order status updated to {instance.status}"
        )
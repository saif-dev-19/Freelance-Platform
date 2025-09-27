from orders.models import Order
from django.db import transaction
from rest_framework.exceptions import PermissionDenied,ValidationError

class OrderServices:
    @staticmethod
    def cancel_order(order,user):
        if user.is_staff:
            order.status = Order.CANCELED
            order.save()
            return order
        
        if order.buyer != user:
            raise PermissionDenied({'detail':"You can only cancel your now order"})
        
        if order.status == Order.DELIVERED:
            raise ValidationError({'deatil':"You can not cancel an order"})
        
        order.status = Order.CANCELED
        order.save()
        return order
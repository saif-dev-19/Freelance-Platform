from django.db import models
from uuid import uuid4
from django.conf import settings
from services.models import Services
from users.models import User

# Create your models here.

class Order(models.Model):
    PENDING = 'Pending'
    IN_PROGRESS = "In_progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

    ORDER_STATUS = [
        (PENDING,'Pending'),
        (IN_PROGRESS,'In_progress'),
        (COMPLETED, 'Completed'),
        (CANCELED, 'Canceled'),
    ]

    id = models.UUIDField(primary_key=True,default=uuid4, editable= False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recived_orders")
    service = models.ForeignKey(Services,on_delete=models.CASCADE,related_name='orders')
    status = models.CharField(max_length=15,choices=ORDER_STATUS, default=PENDING)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    requirements = models.TextField(blank=True,null=True)
    created_at = models.DateField(auto_now_add=True)

    
    def __str__(self):
        return f"order {self.id} by {self.buyer.first_name} {self.status}"
    

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='notifications')
    order =models.ForeignKey(Order,on_delete=models.CASCADE,related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return f"Notification for {self.user.email} = {self.message}"
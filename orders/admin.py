from django.contrib import admin
from orders.models import Order,Notification
# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','buyer','status']

@admin.register(Notification)
class Notifiacation(admin.ModelAdmin):
    list_display = ['id','user','message']
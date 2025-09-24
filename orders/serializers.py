from rest_framework import serializers
from orders.models import Order,Notification
from services.serializers import SimpleUserSerializer
from services.models import Services
from rest_framework.exceptions import PermissionDenied



class SimpleServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model =Services
        fields = ['id','title','seller','price','delivery_time']


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['service','requirements',]
    
    def create(self, validated_data):
        user = self.context['request'].user
        if user.role != 'Buyer':
            raise PermissionDenied("Only Buyers can place orders")
        try:
            buyer_id = self.context.get('buyer_id')
            service= validated_data['service']
            requirements = validated_data['requirements']
            price = service.price

            order = Order.objects.create(buyer_id = buyer_id,service=service,requirements=requirements,total_price =price)

            print(buyer_id)
            print(service)
            return order
        except ValueError as e:
            raise serializers.ValidationError(str(e))
    
class OrderSerializer(serializers.ModelSerializer):
    buyer = SimpleUserSerializer(read_only = True)
    service =SimpleServiceSerializer(read_only = True)
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )
    class Meta:
        model = Order
        fields = ['id','buyer','service','status','total_price','requirements','created_at']
        read_only_fields = ['status','requirements']
    
    def get_total_price(self,obj):
        return obj.service.price
    
class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id','order','message','created_at']
        read_only_fields = ['id']

    def create(self, validated_data):
         user_id = self.context['request'].user

         return Notification.objects.create(user_id = user_id,**validated_data)

class EmptySerializer(serializers.Serializer):
    pass


class SellerTotalEarningSerializer(serializers.Serializer):
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Order
        fields = ['total_earnings']

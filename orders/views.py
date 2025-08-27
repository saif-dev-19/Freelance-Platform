from django.shortcuts import render
from orders.serializers import OrderSerializer,CreateOrderSerlizer,OrderUpdateSerializer,NotificationSerializer,SellerTotalEarningSerializer
from orders.models import Order,Notification
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser,AllowAny
from services import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from services import permissions as customPermission
from django.db.models import Sum
from rest_framework import permissions
# Create your views here.

class OrderViewSet(ModelViewSet):
    http_method_names = ['get','post','delete','patch','head','options']


    # def perform_create(self, serializer):
    #     order = serializer.save()

    #     Notification.objects.create(
    #         user = order.service.seller,
    #         message = f"New Order palced on {order.title}"
    #     )
    
    # def perform_update(self, serializer):
    #     order = serializer.save()
    #     if Order.status == 'Comleted':
    #         Notification.objects.create(
    #         user = order.buyer,
    #         message = f"New Order palced on {order.service.title}"
    #     )
    
    @action(detail=True, methods=['patch'], permission_classes =[customPermission.IsSeller,IsAdminUser])
    def update_status(self,request,pk=None):
        order = self.get_object()
        serializer = OrderUpdateSerializer(order,data=request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status':f'Order Status updated to {request.data['status']}'})


    def get_permissions(self):
        if self.action == 'update_status':
            return [customPermission.OrderIsSeller()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [customPermission.IsBuyer()]
        

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerlizer
        elif self.action == 'update_status':
            return OrderUpdateSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        return {'buyer_id':self.request.user.id}


    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()

        if self.request.user.is_staff:
            return Order.objects.select_related('service').all()
        if self.request.user.role == 'Seller':
            return Order.objects.select_related('service').filter(service__seller = self.request.user)
        if self.request.user.role == 'Buyer':
            return Order.objects.select_related('service').filter(buyer = self.request.user)



# class NotificationViewSet(ModelViewSet):
#     serializer_class = NotificationSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Notification.objects.filter(user = self.request.user)
    
#     def get_serializer_context(self):
#         return {'user_id':self.request.user.id}
    

class BuyerOrderHistory(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [customPermission.IsBuyer,IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer = self.request.user)
    

class totalEarnpermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated and request.user.role == 'Seller'

class SellerTotalEarningsViewSet(ModelViewSet):
    serializer_class = SellerTotalEarningSerializer
    permission_classes = [totalEarnpermission,IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(service__seller = self.request.user,status = Order.COMPLETED)
    
    # def get_serializer(self, *args, **kwargs):
    #     total_earnings = self.get_queryset().aaggregate(total = Sum('total_price'))['total'] or 0
    #     return {'total_earnings':total_earnings}

    def list(self, request):
        total = self.get_queryset().aggregate(total=Sum('total_price'))['total'] or 0 
        serializer = SellerTotalEarningSerializer({'total_earnings': total})
        return Response(serializer.data)
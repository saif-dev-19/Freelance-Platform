from django.shortcuts import render
from orders.serializers import OrderSerializer,OrderUpdateSerializer,NotificationSerializer,SellerTotalEarningSerializer,EmptySerializer,CreateOrderSerializer
from orders.models import Order,Notification
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser,AllowAny
from rest_framework.exceptions import PermissionDenied
from services import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from services import permissions as customPermission
from django.db.models import Sum
from rest_framework import permissions
from orders.permissions import OrderPermissons
from orders.services import OrderServices
from rest_framework.decorators import api_view
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework import status
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.conf import settings as django_settings
from rest_framework.views import APIView 
# Create your views here.

class OrderViewSet(ModelViewSet):
    permission_classes = [OrderPermissons]
    http_method_names = ['get','post','delete','patch','head','options']


    def perform_create(self, serializer):
        if self.request.user.role != 'Buyer':
            raise PermissionDenied("Only Buyers can place orders")
        serializer.save(buyer_id=self.request.user.id)

    @action(detail=True, methods=['patch'], permission_classes =[customPermission.IsSeller,IsAdminUser])
    def update_status(self,request,pk=None):
        order = self.get_object()
        serializer = OrderUpdateSerializer(order,data=request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status':f'Order Status updated to {request.data['status']}'})
    
    @action(detail=True, methods=['post'], permission_classes =[IsAuthenticated])
    def cancel(self,request,pk=None): #cancel action er maddome order cancel kora jabe post method e
        order = self.get_object()
        OrderServices.cancel_order(order = order, user = request.user)
        return Response({'status':'Order Canceled'})

    def get_permissions(self):
        if self.action in ['update_status','destroy']:
            return [IsAdminUser()]
        if self.action == 'cancel':
            return [IsAuthenticated()] 
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'cancel':
            return EmptySerializer
        if self.request.method == 'POST':
            return CreateOrderSerializer
        if self.request.method == 'PATCH':
            return OrderUpdateSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
         return {
        'request': self.request,
        'buyer_id': self.request.user.id
        }


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
    permission_classes = [totalEarnpermission]

    def get_queryset(self):
        return Order.objects.filter(
            service__seller=self.request.user,
            status=Order.COMPLETED
        )


    def list(self, request):
        total = self.get_queryset().aggregate(total=Sum('total_price'))['total'] or 0
        print(total)
        serializer = self.get_serializer({'total_earnings': total})
        return Response(serializer.data)
    
    # def get_serializer(self, *args, **kwargs):
    #     total_earnings = self.get_queryset().aaggregate(total = Sum('total_price'))['total'] or 0
    #     return {'total_earnings':total_earnings}


class HasOrderedService(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request,service_id):
        user = request.user
        has_ordered = Order.objects.filter(
            service_id = service_id,
            buyer = user,
            status = "Completed"
        ).exists()
        return Response({"has_orderes":has_ordered})



@api_view(["POST"])
def initiate_payment(request):
    user = request.user
    amount = request.data.get('amount')
    order_id = request.data.get('orderID')

    settings = { 'store_id': 'codur68d8bc8208748', 'store_pass': 'codur68d8bc8208748@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = f"txn_{order_id}"
    post_body['success_url'] = f"{django_settings.BACKEND_URL}/api/payment/success/"
    post_body['fail_url'] = f"{django_settings.BACKEND_URL}/api/payment/fail/"
    post_body['cancel_url'] = f"{django_settings.BACKEND_URL}/api/dashboard/orders/"
    post_body['emi_option'] = 0
    post_body['cus_name'] = f"{user.first_name} {user.last_name}"
    post_body['cus_email'] = f"{user.email}"
    post_body['cus_phone'] = f"{user.phone_number}"
    post_body['cus_add1'] = f"{user.address}"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Virtual Bazar Services"
    post_body['product_category'] = "General"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body) # API response

    if response.get("status") == "SUCCESS":
        return Response({"payment_url": response['GatewayPageURL']})
    return Response({"error":"payment initiation failed"},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def payment_success(request):
    print("Inside success")
    order_id = request.data.get("tran_id").split('_')[1]
    order = Order.objects.get(id=order_id)
    order.status = "In_progress"
    order.save()
    return HttpResponseRedirect(f"{django_settings.FRONTEND_URL}/dashboard/orders/")

@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(f"{django_settings.FRONTEND_URL}/dashboard/orders/")

@api_view(['POST'])
def payment_fail(request):
    return HttpResponseRedirect(f"{django_settings.FRONTEND_URL}/dashboard/orders/")



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seller_recent_orders(request):
    seller = request.user

    orders = (
        Order.objects.filter(service__seller=seller)
        .select_related('buyer', 'service')
        .order_by('-created_at')[:5]
    )

    data = [
        {
            "id": f"#ORD-{order.id}",
            "buyer": order.buyer.get_full_name() or order.buyer.email,
            "service": order.service.title,
            "amount": f"${order.total_price}",
            "status": order.status,
            "time": f"{order.created_at}"
        }
        for order in orders
    ]

    return Response(data)

from django.shortcuts import render
from orders.serializers import OrderSerializer,NotificationSerializer,SellerTotalEarningSerializer,EmptySerializer,CreateOrderSerializer,DeliverySerializer,RevisionSerializer
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
    http_method_names = ['get','post','delete','head','options']


    def perform_create(self, serializer):
        if self.request.user.role != 'Buyer':
            raise PermissionDenied("Only Buyers can place orders")
        serializer.save(buyer_id=self.request.user.id)

    @action(detail=True, methods=['post'])
    def deliver(self,request,pk=None):
        order = self.get_object()
        if order.status != Order.IN_PROGRESS:
            return Response({'detail':'Only in-progress orders can be delivered.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.delivery_message = serializer.validated_data['message']
        order.delivery_url = serializer.validated_data.get('url', '')
        order.revision_feedback = ''
        order.status = Order.DELIVERED
        order.save()
        return Response(OrderSerializer(order, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def accept_delivery(self,request,pk=None):
        order = self.get_object()
        if order.status != Order.DELIVERED:
            return Response({'detail':'Only delivered orders can be accepted.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.COMPLETED
        order.save()
        return Response(OrderSerializer(order, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def request_revision(self,request,pk=None):
        order = self.get_object()
        if order.status != Order.DELIVERED:
            return Response({'detail':'A revision can only be requested for a delivered order.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RevisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.revision_feedback = serializer.validated_data['feedback']
        order.status = Order.IN_PROGRESS
        order.save()
        return Response(OrderSerializer(order, context={'request': request}).data)
    
    @action(detail=True, methods=['post'], permission_classes =[IsAuthenticated])
    def cancel(self,request,pk=None): #cancel action er maddome order cancel kora jabe post method e
        order = self.get_object()
        OrderServices.cancel_order(order = order, user = request.user)
        return Response({'status':'Order Canceled'})

    def get_permissions(self):
        if self.action in ['deliver', 'accept_delivery', 'request_revision', 'cancel']:
            return [IsAuthenticated(), OrderPermissons()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'cancel':
            return EmptySerializer
        if self.request.method == 'POST':
            return CreateOrderSerializer
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
            return (
                Order.objects
                .select_related('buyer', 'service__seller')
                .prefetch_related('service__images')
                .order_by('-created_at', '-id')
            )
        if self.request.user.role == 'Seller':
            return (
                Order.objects
                .select_related('buyer', 'service__seller')
                .prefetch_related('service__images')
                .filter(service__seller=self.request.user)
                .order_by('-created_at', '-id')
            )
        if self.request.user.role == 'Buyer':
            return (
                Order.objects
                .select_related('buyer', 'service__seller')
                .prefetch_related('service__images')
                .filter(buyer=self.request.user)
                .order_by('-created_at', '-id')
            )



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
        return (
            Order.objects
            .select_related('buyer', 'service__seller')
            .prefetch_related('service__images')
            .filter(buyer=self.request.user)
            .order_by('-created_at', '-id')
        )
    

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
        buyer_orders = Order.objects.filter(
            service_id = service_id,
            buyer = user
        )
        order = buyer_orders.order_by('-created_at', '-id').first()
        has_ordered = buyer_orders.filter(status=Order.COMPLETED).exists()
        return Response({
            "has_ordered": has_ordered,
            "has_orderes": has_ordered,
            "order_status": order.status if order else None,
        })



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

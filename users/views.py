from django.shortcuts import render

# Create your views here.

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from orders.models import Order
from django.db.models import Sum
from rest_framework.viewsets import ModelViewSet
from .models import User
from .serializers import UserSerializer

User = get_user_model()

@api_view(['GET'])
def admin_dashboard_summary(request):

    totals = User.objects.aggregate(
        total_users=Count('id'),
        total_sellers=Count('id', filter=Q(role='Seller')),
        total_buyers=Count('id', filter=Q(role='Buyer')),
    )


    sellers = list(
        User.objects.filter(role="Seller").values("id", "first_name", "last_name", "email","last_login","date_joined")
    )
    buyers = list(
        User.objects.filter(role="Buyer").values("id", "first_name", "last_name", "email","last_login","date_joined")
    )

    top_sellers = (
    User.objects.filter(role="Seller")
    .annotate(service_count=Count("services"))
    .order_by("-service_count")[:3]
    .values("id", "first_name", "last_name", "email", "service_count","last_login","date_joined")
    )

    top_buyers = (
        User.objects.filter(role="Buyer")
        .annotate(order_count=Count("recived_orders"))  
        .order_by("-order_count")[:3]
        .values("id", "first_name", "last_name", "email", "order_count","last_login","date_joined") 
    )


    total_revenue = Order.objects.filter(status="Completed").aggregate(
        total=Sum("total_price")
    )["total"] or 0

    return Response({
        "total_users": totals['total_users'],
        "total_sellers": totals['total_sellers'],
        "total_buyers": totals['total_buyers'],
        "sellers": sellers,
        "buyers": buyers,
        "top_sellers": list(top_sellers),
        "top_buyers": list(top_buyers),
        "total_revenue":total_revenue
    })


class UserViewSet(ModelViewSet):
    queryset = User.objects.only(
        'id', 'email', 'first_name', 'last_name', 'role', 'address', 'phone_number'
    ).order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
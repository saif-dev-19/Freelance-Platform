from django.shortcuts import render

# Create your views here.

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

User = get_user_model()
from orders.models import Order  
from services.models import Services

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_summary(request):

    total_users = User.objects.count()
    total_sellers = User.objects.filter(role="Seller").count()
    total_buyers = User.objects.filter(role="Buyer").count()


    sellers = list(
        User.objects.filter(role="Seller").values("id", "first_name", "last_name", "email")
    )
    buyers = list(
        User.objects.filter(role="Buyer").values("id", "first_name", "last_name", "email")
    )

    top_sellers = (
        User.objects.filter(role="Seller")
        .annotate(service_count=Count("services"))
        .order_by("-service_count")[:5]
        .values("id", "first_name", "last_name", "service_count")
    )

    top_buyers = (
        User.objects.filter(role="Buyer")
        .annotate(order_count=Count("recived_orders"))
        .order_by("-order_count")[:5]
        .values("id", "first_name", "last_name", "order_count")
    )

    return Response({
        "total_users": total_users,
        "total_sellers": total_sellers,
        "total_buyers": total_buyers,
        "sellers": sellers,
        "buyers": buyers,
        "top_sellers": list(top_sellers),
        "top_buyers": list(top_buyers)
    })

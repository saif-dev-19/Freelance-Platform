from django.urls import path,include
from rest_framework.routers import DefaultRouter
from services import views
from orders import views as orderview
from rest_framework_nested import routers
from orders.views import initiate_payment,payment_success,payment_fail,payment_cancel,HasOrderedService,seller_recent_orders
from users.views import admin_dashboard_summary,UserViewSet


router = routers.DefaultRouter()
router.register("services",views.ServiceViewSet,basename="services")
router.register("categories",views.CategoryViewSet)
router.register("orders",orderview.OrderViewSet, basename= "orders")
# router.register('notifications',order.NotificationViewSet, basename="notifications")
router.register('buyer-order',orderview.BuyerOrderHistory, basename='buyer-order')
router.register('seller-earnings',orderview.SellerTotalEarningsViewSet, basename="seller-earnings")
router.register('buyer-reviews',views.BuyerReviews, basename="buyer-reviews"),
router.register('seller-services',views.SellerService,basename='seller-services'),
router.register('users',UserViewSet,basename="users")


service_router = routers.NestedDefaultRouter(router, 'services',lookup = 'service')
service_router.register('reviews',views.ReviewViewSet, basename='service-review')
service_router.register('images',views.ServiceImageViewSet, basename="service-images")

# urlpatterns = router.urls

urlpatterns = [
    path('',include(router.urls)),
    path('',include(service_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path("payment/initiate/", initiate_payment, name="initiate-payment"),
    path("payment/success/", payment_success, name="payment-success"),
    path("payment/fail/", payment_fail, name="payment-fail"),
    path("payment/cancel/", payment_cancel, name="payment-cancel"),
    path("orders/has-ordered/<int:service_id>/",HasOrderedService.as_view()),
    path("users-summary/", admin_dashboard_summary,name="users-summary"),
    path("recent-orders/",seller_recent_orders ,name="recent-orders"),
]
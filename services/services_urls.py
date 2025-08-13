from django.urls import path
from services import views

urlpatterns = [
    path('',views.ServiceViewSet.as_view(), name = 'service-list'),
    path('<int:pk>/',views.ServiceDetails.as_view(), name= 'service-list')

]

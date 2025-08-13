from django.urls import path
from services import views

urlpatterns = [
    path('',views.CategoryList.as_view(), name= 'category-list'),
    path('<int:pk>/',views.CategoryDetails.as_view(), name= 'view_specific_category')

]
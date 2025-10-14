from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from services.models import Services,Category
from services.serializers import ServiceSerializer,CategorySerializer,ReviewSerializer,ServiceImageSerializer
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from services.models import Review,ServiceImage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter,SearchFilter
from services.pagination import DefaultPagination
from rest_framework.permissions import IsAuthenticated
from services.permissions import IsSeller,IsAdminOrReadOnly,IsBuyer,ReviewAuthorOrReadOnly
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.exceptions import ValidationError
from services.filters import ServiceFilter
# Create your views here.


class ServiceViewSet(ModelViewSet):
    serializer_class =  ServiceSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    # filterset_class = ServiceFilter
    ordering_fields = ['price']
    filterset_class = ServiceFilter
    search_fields = ['title','category__name']
    pagination_class = DefaultPagination
    permission_classes = [IsSeller]

    def perform_create(self, serializer):
        serializer.save(seller = self.request.user)

    def get_queryset(self):
          return Services.objects.prefetch_related('images').all()

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(service_count = Count('services')).all()
    serializer_class =CategorySerializer
    permission_classes = [IsAdminOrReadOnly]



class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsBuyer]

    def perform_create(self, serializer): # by this method  service_id and buyer_id, I pass in serializer for buyer reviews CREATE
        service_id = self.kwargs.get('service_pk')
        serializer.save(buyer = self.request.user,service_id = service_id)

    def perform_update(self, serializer): # by this method  buyer_id, I pass in serializer for buyer reviews update otherwise error
        serializer.save(buyer = self.request.user)

    # def get_serializer_context(self):
    #     return {'service_id':self.kwargs.get('service_pk')} 
    def get_queryset(self):
        return Review.objects.filter(service_id = self.kwargs.get('service_pk'))
    


class ServiceImageViewSet(ModelViewSet):
    serializer_class = ServiceImageSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        service = Services.objects.get(pk=self.kwargs.get('service_pk'))
        return ServiceImage.objects.filter(service=service)

    
    def perform_create(self, serializer):
        service = Services.objects.get(pk= self.kwargs.get('service_pk'))
        
        if service.seller != self.request.user:
            raise ValidationError("You can't have permission to add image ")

        serializer.save(service = service)
    
class BuyerReviews(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsBuyer,IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(buyer = self.request.user)

